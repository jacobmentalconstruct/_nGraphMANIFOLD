"""Side harness for lens-based evidence-bag retrieval over project docs."""

from __future__ import annotations

import json
import math
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.representation import SemanticObject

from .project_documents import DEFAULT_PROJECT_DOCUMENT_PROFILE, ingest_project_documents
from .project_query_lens_selector import (
    AUTO_LENS_PROFILE,
    ProjectQueryLensSelection,
    manual_project_query_lens_selection,
    select_project_query_lens,
)
from .seed_fitness import SeedFitnessPolicy, SeedSearchCandidate, rank_seed_candidates

PROJECT_QUERY_LENS_BAG_VERSION = "v2"
DEFAULT_LENS_PROFILE = "balanced"
DEFAULT_SEMANTIC_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHAR_BUDGET = 2400
DEFAULT_MAX_ITEMS = 8
DEFAULT_MAX_SEEDS = 8
DEFAULT_MAX_NODES = 80
DEFAULT_RADIUS = 2
DEFAULT_PROPAGATION_ITERATIONS = 2
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")
COMMON_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "do",
    "for",
    "how",
    "if",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


@dataclass(frozen=True)
class LensProfileConfig:
    """Weight coefficients for one lens profile."""

    semantic_similarity: float
    structural_proximity: float
    identity_relevance: float
    adjacency_support: float
    exact_match: float
    propagation_decay: float
    neighborhood_density_bonus: float

    def to_dict(self) -> dict[str, float]:
        return {
            "semantic_similarity": self.semantic_similarity,
            "structural_proximity": self.structural_proximity,
            "identity_relevance": self.identity_relevance,
            "adjacency_support": self.adjacency_support,
            "exact_match": self.exact_match,
            "propagation_decay": self.propagation_decay,
            "neighborhood_density_bonus": self.neighborhood_density_bonus,
        }


LENS_PROFILES: dict[str, LensProfileConfig] = {
    "balanced": LensProfileConfig(0.30, 0.25, 0.15, 0.15, 0.15, 0.50, 0.05),
    "semantic_heavy": LensProfileConfig(0.55, 0.10, 0.10, 0.10, 0.15, 0.60, 0.03),
    "structure_heavy": LensProfileConfig(0.10, 0.50, 0.15, 0.20, 0.05, 0.40, 0.08),
    "provenance_heavy": LensProfileConfig(0.10, 0.20, 0.40, 0.20, 0.10, 0.30, 0.04),
    "exact_match_heavy": LensProfileConfig(0.10, 0.10, 0.10, 0.10, 0.60, 0.70, 0.02),
    "neighborhood_support_heavy": LensProfileConfig(0.15, 0.15, 0.10, 0.45, 0.15, 0.40, 0.10),
}
LENS_PROFILE_NAMES = tuple(sorted(LENS_PROFILES))


@dataclass(frozen=True)
class LensSeedCandidate:
    """Seed candidate for the side harness."""

    semantic_id: str
    source_ref: str
    kind: str
    heading_trail: tuple[str, ...]
    preview: str
    lexical_score: float
    semantic_score: float
    exact_score: float
    combined_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_id": self.semantic_id,
            "source_ref": self.source_ref,
            "kind": self.kind,
            "heading_trail": list(self.heading_trail),
            "preview": self.preview,
            "lexical_score": round(self.lexical_score, 4),
            "semantic_score": round(self.semantic_score, 4),
            "exact_score": round(self.exact_score, 4),
            "combined_score": round(self.combined_score, 4),
        }


@dataclass(frozen=True)
class LensProjectedNode:
    """Projected node with lens-scoring diagnostics."""

    semantic_id: str
    source_ref: str
    kind: str
    heading_trail: tuple[str, ...]
    depth: int
    preview: str
    score: float
    score_components: dict[str, float]
    relation_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_id": self.semantic_id,
            "source_ref": self.source_ref,
            "kind": self.kind,
            "heading_trail": list(self.heading_trail),
            "depth": self.depth,
            "preview": self.preview,
            "score": round(self.score, 4),
            "score_components": {key: round(value, 4) for key, value in self.score_components.items()},
            "relation_count": self.relation_count,
        }


@dataclass(frozen=True)
class LensEvidenceBagItem:
    """One packed evidence item from the side harness."""

    semantic_id: str
    source_ref: str
    kind: str
    heading_trail: tuple[str, ...]
    depth: int
    source_role: str
    content: str
    score: float
    density: float
    is_truncated: bool
    score_components: dict[str, float]

    @property
    def weight(self) -> int:
        return len(self.content)

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_id": self.semantic_id,
            "source_ref": self.source_ref,
            "kind": self.kind,
            "heading_trail": list(self.heading_trail),
            "depth": self.depth,
            "source_role": self.source_role,
            "content": self.content,
            "score": round(self.score, 4),
            "density": round(self.density, 6),
            "weight": self.weight,
            "is_truncated": self.is_truncated,
            "score_components": {key: round(value, 4) for key, value in self.score_components.items()},
        }


@dataclass(frozen=True)
class ProjectQueryLensBagRun:
    """Inspectable side-harness run for one project query."""

    version: str
    project_root: str
    document_profile: str
    document_paths: tuple[str, ...]
    cartridge_path: str
    semantic_model_name: str
    query: str
    requested_lens_profile: str
    lens_profile: str
    lens_selection: ProjectQueryLensSelection
    lens_config: LensProfileConfig
    corpus_object_count: int
    corpus_relation_count: int
    baseline_candidates: tuple[SeedSearchCandidate, ...]
    seed_candidates: tuple[LensSeedCandidate, ...]
    projected_node_count: int
    projected_edge_count: int
    top_projected_nodes: tuple[LensProjectedNode, ...]
    bag_items: tuple[LensEvidenceBagItem, ...]
    bag_char_budget: int
    bag_total_chars: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "document_profile": self.document_profile,
            "document_paths": list(self.document_paths),
            "cartridge_path": self.cartridge_path,
            "semantic_model_name": self.semantic_model_name,
            "query": self.query,
            "requested_lens_profile": self.requested_lens_profile,
            "lens_profile": self.lens_profile,
            "lens_selection": self.lens_selection.to_dict(),
            "lens_config": self.lens_config.to_dict(),
            "corpus_object_count": self.corpus_object_count,
            "corpus_relation_count": self.corpus_relation_count,
            "baseline_candidates": [candidate.to_dict() for candidate in self.baseline_candidates],
            "seed_candidates": [candidate.to_dict() for candidate in self.seed_candidates],
            "projected_node_count": self.projected_node_count,
            "projected_edge_count": self.projected_edge_count,
            "top_projected_nodes": [node.to_dict() for node in self.top_projected_nodes],
            "bag_items": [item.to_dict() for item in self.bag_items],
            "bag_char_budget": self.bag_char_budget,
            "bag_total_chars": self.bag_total_chars,
            "bag_utilization": round(self.bag_total_chars / max(self.bag_char_budget, 1), 4),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class ProjectQueryLensBagWorkspace:
    """Reusable corpus and embedding state for repeated side-harness runs."""

    project_root: str
    document_profile: str
    document_paths: tuple[str, ...]
    cartridge_path: str
    semantic_model_name: str
    objects: tuple[SemanticObject, ...]
    object_map: dict[str, SemanticObject]
    manifest_relation_count: int
    lexical_vectorizer: TfidfVectorizer
    lexical_matrix: Any
    semantic_model: SentenceTransformer
    semantic_matrix: np.ndarray
    semantic_index: dict[str, int]
    cartridge: SemanticCartridge
    outgoing_edges: dict[str, tuple[_GraphEdge, ...]]
    incoming_edges: dict[str, tuple[_GraphEdge, ...]]


@dataclass
class _GraphEdge:
    from_id: str
    to_id: str
    predicate: str
    weight: float


@dataclass
class _WorkingNode:
    obj: SemanticObject
    depth: int
    seed_score: float
    score: float = 0.0
    score_components: dict[str, float] | None = None


def default_project_query_lens_bag_path(project_root: Path | str) -> Path:
    """Return the default artifact path for the side harness."""
    return Path(project_root) / "data" / "mcp_inspection" / "project_query_lens_bag.json"


def build_project_query_lens_bag_workspace(
    project_root: Path | str,
    *,
    document_profile: str = DEFAULT_PROJECT_DOCUMENT_PROFILE,
    semantic_model_name: str = DEFAULT_SEMANTIC_MODEL_NAME,
) -> ProjectQueryLensBagWorkspace:
    """Build reusable corpus state for repeated side-harness queries."""
    root = Path(project_root).resolve()
    corpus = ingest_project_documents(root, document_profile=document_profile)
    cartridge = SemanticCartridge(corpus.cartridge_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = tuple(cartridge.all_objects())
    manifest = cartridge.manifest()
    if not objects:
        raise ValueError("Project document corpus is empty")

    candidate_texts = [_candidate_text(obj) for obj in objects]
    semantic_texts = [_semantic_structured_text(obj) for obj in objects]
    lexical_vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
    lexical_matrix = lexical_vectorizer.fit_transform(candidate_texts)
    semantic_model = SentenceTransformer(semantic_model_name)
    semantic_matrix = semantic_model.encode(
        semantic_texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    object_map = {obj.semantic_id: obj for obj in objects}
    semantic_index = {obj.semantic_id: index for index, obj in enumerate(objects)}
    outgoing_edges: dict[str, list[_GraphEdge]] = {}
    incoming_edges: dict[str, list[_GraphEdge]] = {}
    for obj in objects:
        for relation in cartridge.relations_for(obj.semantic_id):
            target_ref = str(relation.get("target_ref") or "")
            if target_ref not in object_map:
                continue
            edge = _GraphEdge(
                from_id=obj.semantic_id,
                to_id=target_ref,
                predicate=str(relation.get("predicate") or ""),
                weight=float(relation.get("weight", 1.0)),
            )
            outgoing_edges.setdefault(obj.semantic_id, []).append(edge)
            incoming_edges.setdefault(target_ref, []).append(edge)

    return ProjectQueryLensBagWorkspace(
        project_root=str(root),
        document_profile=corpus.document_profile,
        document_paths=corpus.document_paths,
        cartridge_path=corpus.cartridge_path,
        semantic_model_name=semantic_model_name,
        objects=objects,
        object_map=object_map,
        manifest_relation_count=manifest.relation_count,
        lexical_vectorizer=lexical_vectorizer,
        lexical_matrix=lexical_matrix,
        semantic_model=semantic_model,
        semantic_matrix=semantic_matrix,
        semantic_index=semantic_index,
        cartridge=cartridge,
        outgoing_edges={key: tuple(value) for key, value in outgoing_edges.items()},
        incoming_edges={key: tuple(value) for key, value in incoming_edges.items()},
    )


def run_project_query_lens_bag(
    project_root: Path | str,
    query: str,
    *,
    document_profile: str = DEFAULT_PROJECT_DOCUMENT_PROFILE,
    lens_profile: str = DEFAULT_LENS_PROFILE,
    semantic_model_name: str = DEFAULT_SEMANTIC_MODEL_NAME,
    max_seeds: int = DEFAULT_MAX_SEEDS,
    radius: int = DEFAULT_RADIUS,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_items: int = DEFAULT_MAX_ITEMS,
    char_budget: int = DEFAULT_CHAR_BUDGET,
    workspace: ProjectQueryLensBagWorkspace | None = None,
) -> ProjectQueryLensBagRun:
    """Run the side harness over the bounded project-doc corpus."""
    active_workspace = workspace or build_project_query_lens_bag_workspace(
        project_root,
        document_profile=document_profile,
        semantic_model_name=semantic_model_name,
    )

    if lens_profile == AUTO_LENS_PROFILE:
        lens_selection = select_project_query_lens(query)
        resolved_lens_profile = lens_selection.selected_lens_profile
    else:
        lens_selection = manual_project_query_lens_selection(lens_profile)
        resolved_lens_profile = lens_selection.selected_lens_profile

    if resolved_lens_profile not in LENS_PROFILES:
        raise ValueError(f"Unsupported lens profile: {lens_profile}")
    lens = LENS_PROFILES[resolved_lens_profile]

    lexical_query = active_workspace.lexical_vectorizer.transform([query])
    lexical_scores = np.asarray((active_workspace.lexical_matrix @ lexical_query.T).todense()).ravel()
    query_vector = active_workspace.semantic_model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
    semantic_scores = np.dot(active_workspace.semantic_matrix, query_vector)
    exact_scores = np.asarray([_exact_match_score(query, obj) for obj in active_workspace.objects], dtype=float)
    combined_seed_scores = (
        _normalize(lexical_scores) * 0.45
        + _normalize(semantic_scores) * 0.45
        + _normalize(exact_scores) * 0.10
    )

    seed_candidates = _top_seed_candidates(
        list(active_workspace.objects),
        lexical_scores,
        semantic_scores,
        exact_scores,
        combined_seed_scores,
        limit=max(1, max_seeds),
    )
    seed_score_map = {
        candidate.semantic_id: candidate.combined_score
        for candidate in seed_candidates
    }
    baseline_candidates = tuple(
        rank_seed_candidates(
            list(active_workspace.objects),
            query,
            limit=5,
            policy=SeedFitnessPolicy(seed_text_hint=query, question=query),
        )
    )

    visited_ids, graph_edges, depth_map = _project_neighborhood(
        seed_candidates=seed_candidates,
        outgoing_edges=active_workspace.outgoing_edges,
        incoming_edges=active_workspace.incoming_edges,
        radius=max(0, radius),
        max_nodes=max(1, max_nodes),
    )
    working_nodes = {
        semantic_id: _WorkingNode(
            obj=active_workspace.object_map[semantic_id],
            depth=depth_map[semantic_id],
            seed_score=seed_score_map.get(semantic_id, 0.0),
        )
        for semantic_id in visited_ids
    }

    _score_projection(
        working_nodes=working_nodes,
        graph_edges=graph_edges,
        query=query,
        query_vector=query_vector,
        lens=lens,
        semantic_matrix=active_workspace.semantic_matrix,
        semantic_index=active_workspace.semantic_index,
    )
    _propagate_scores(
        working_nodes=working_nodes,
        graph_edges=graph_edges,
        lens=lens,
        iterations=DEFAULT_PROPAGATION_ITERATIONS,
    )

    bag_items = _compose_bag(
        working_nodes=working_nodes,
        seed_ids={candidate.semantic_id for candidate in seed_candidates},
        char_budget=max(200, char_budget),
        max_items=max(1, max_items),
    )
    ranked_nodes = sorted(
        working_nodes.items(),
        key=lambda item: item[1].score,
        reverse=True,
    )
    top_projected_nodes = tuple(
        LensProjectedNode(
            semantic_id=semantic_id,
            source_ref=_source_ref(node.obj),
            kind=node.obj.kind,
            heading_trail=_heading_trail(node.obj),
            depth=node.depth,
            preview=_preview(node.obj.content),
            score=node.score,
            score_components=node.score_components or {},
            relation_count=_relation_count(node.obj, graph_edges),
        )
        for semantic_id, node in ranked_nodes[:10]
    )

    return ProjectQueryLensBagRun(
        version=PROJECT_QUERY_LENS_BAG_VERSION,
        project_root=active_workspace.project_root,
        document_profile=active_workspace.document_profile,
        document_paths=active_workspace.document_paths,
        cartridge_path=active_workspace.cartridge_path,
        semantic_model_name=active_workspace.semantic_model_name,
        query=query,
        requested_lens_profile=lens_profile,
        lens_profile=resolved_lens_profile,
        lens_selection=lens_selection,
        lens_config=lens,
        corpus_object_count=len(active_workspace.objects),
        corpus_relation_count=active_workspace.manifest_relation_count,
        baseline_candidates=baseline_candidates,
        seed_candidates=tuple(seed_candidates),
        projected_node_count=len(working_nodes),
        projected_edge_count=len(graph_edges),
        top_projected_nodes=top_projected_nodes,
        bag_items=tuple(bag_items),
        bag_char_budget=max(200, char_budget),
        bag_total_chars=sum(item.weight for item in bag_items),
    )


def save_project_query_lens_bag_run(
    run: ProjectQueryLensBagRun,
    output_path: Path | str,
) -> Path:
    """Persist one side-harness run to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.to_json(), encoding="utf-8")
    return path


def _top_seed_candidates(
    objects: list[SemanticObject],
    lexical_scores: np.ndarray,
    semantic_scores: np.ndarray,
    exact_scores: np.ndarray,
    combined_scores: np.ndarray,
    *,
    limit: int,
) -> list[LensSeedCandidate]:
    ranked_indices = np.argsort(combined_scores)[::-1][: max(1, limit)]
    return [
        LensSeedCandidate(
            semantic_id=objects[index].semantic_id,
            source_ref=_source_ref(objects[index]),
            kind=objects[index].kind,
            heading_trail=_heading_trail(objects[index]),
            preview=_preview(objects[index].content),
            lexical_score=float(lexical_scores[index]),
            semantic_score=float(semantic_scores[index]),
            exact_score=float(exact_scores[index]),
            combined_score=float(combined_scores[index]),
        )
        for index in ranked_indices
    ]


def _project_neighborhood(
    *,
    seed_candidates: list[LensSeedCandidate],
    outgoing_edges: dict[str, tuple[_GraphEdge, ...]],
    incoming_edges: dict[str, tuple[_GraphEdge, ...]],
    radius: int,
    max_nodes: int,
) -> tuple[set[str], list[_GraphEdge], dict[str, int]]:
    visited: set[str] = set()
    depth_map: dict[str, int] = {}
    edges: list[_GraphEdge] = []
    seen_edges: set[tuple[str, str, str]] = set()
    frontier: deque[tuple[str, int]] = deque()

    for seed in seed_candidates:
        visited.add(seed.semantic_id)
        depth_map[seed.semantic_id] = 0
        frontier.append((seed.semantic_id, 0))

    while frontier and len(visited) < max_nodes:
        current_id, depth = frontier.popleft()
        if depth >= radius:
            continue
        for edge in outgoing_edges.get(current_id, ()) + incoming_edges.get(current_id, ()):
            if edge.from_id == current_id:
                neighbor_id = edge.to_id
            else:
                neighbor_id = edge.from_id
            edge_key = (edge.from_id, edge.to_id, edge.predicate)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append(edge)
            if neighbor_id not in visited and len(visited) < max_nodes:
                visited.add(neighbor_id)
                depth_map[neighbor_id] = depth + 1
                frontier.append((neighbor_id, depth + 1))

    return visited, edges, depth_map


def _score_projection(
    *,
    working_nodes: dict[str, _WorkingNode],
    graph_edges: list[_GraphEdge],
    query: str,
    query_vector: np.ndarray,
    lens: LensProfileConfig,
    semantic_matrix: np.ndarray,
    semantic_index: dict[str, int],
) -> None:
    adjacency: dict[str, list[tuple[str, float]]] = {}
    for edge in graph_edges:
        adjacency.setdefault(edge.from_id, []).append((edge.to_id, edge.weight))
        adjacency.setdefault(edge.to_id, []).append((edge.from_id, edge.weight))

    max_depth = max((node.depth for node in working_nodes.values()), default=0)
    normalized_query = query.lower().strip()
    query_terms = _tokenize_query(query)

    for semantic_id, node in working_nodes.items():
        obj = node.obj
        text_lower = _candidate_text(obj).lower()
        neighbors = adjacency.get(semantic_id, [])
        semantic_similarity = 0.0
        index = semantic_index.get(semantic_id)
        if index is not None:
            semantic_similarity = max(0.0, float(np.dot(semantic_matrix[index], query_vector)))

        if max_depth <= 0:
            structural_proximity = 1.0
        else:
            structural_proximity = 1.0 - (node.depth / max_depth)

        identity_relevance = node.seed_score
        if neighbors:
            adjacency_support = sum(
                working_nodes.get(neighbor_id, _WorkingNode(obj=obj, depth=0, seed_score=0.0)).seed_score
                for neighbor_id, _weight in neighbors
            ) / len(neighbors)
        else:
            adjacency_support = 0.0

        exact_match = 0.0
        if normalized_query and normalized_query in text_lower:
            exact_match = min(1.0, (len(normalized_query) / max(len(text_lower), 1)) + 0.5)
        else:
            overlap = len(query_terms & _tokenize_query(_candidate_text(obj)))
            if query_terms:
                exact_match = overlap / len(query_terms)

        score = (
            lens.semantic_similarity * semantic_similarity
            + lens.structural_proximity * structural_proximity
            + lens.identity_relevance * identity_relevance
            + lens.adjacency_support * adjacency_support
            + lens.exact_match * exact_match
        )
        density_bonus = min(len(neighbors) * lens.neighborhood_density_bonus, 0.2)
        score += density_bonus
        components = {
            "semantic_similarity": semantic_similarity,
            "structural_proximity": structural_proximity,
            "identity_relevance": identity_relevance,
            "adjacency_support": adjacency_support,
            "exact_match": exact_match,
            "neighborhood_density": density_bonus,
        }

        if node.depth > 0:
            decay = lens.propagation_decay ** node.depth
            score *= decay
            components["decay_factor"] = decay

        node.score = round(score, 6)
        node.score_components = {key: round(value, 6) for key, value in components.items()}


def _propagate_scores(
    *,
    working_nodes: dict[str, _WorkingNode],
    graph_edges: list[_GraphEdge],
    lens: LensProfileConfig,
    iterations: int,
) -> None:
    adjacency: dict[str, list[tuple[str, float]]] = {}
    for edge in graph_edges:
        adjacency.setdefault(edge.from_id, []).append((edge.to_id, edge.weight))
        adjacency.setdefault(edge.to_id, []).append((edge.from_id, edge.weight))

    for iteration in range(max(0, iterations)):
        deltas: dict[str, float] = {}
        for semantic_id, node in working_nodes.items():
            neighbors = adjacency.get(semantic_id, [])
            if not neighbors:
                continue
            influence = 0.0
            for neighbor_id, edge_weight in neighbors:
                neighbor = working_nodes.get(neighbor_id)
                if neighbor is None:
                    continue
                influence += neighbor.score * edge_weight
            avg_influence = influence / len(neighbors)
            deltas[semantic_id] = avg_influence * lens.propagation_decay * (0.5**iteration)

        for semantic_id, delta in deltas.items():
            node = working_nodes[semantic_id]
            node.score = round(node.score + delta, 6)
            components = dict(node.score_components or {})
            components["propagation_boost"] = round(components.get("propagation_boost", 0.0) + delta, 6)
            node.score_components = components


def _compose_bag(
    *,
    working_nodes: dict[str, _WorkingNode],
    seed_ids: set[str],
    char_budget: int,
    max_items: int,
) -> list[LensEvidenceBagItem]:
    ranked = sorted(working_nodes.values(), key=lambda node: node.score, reverse=True)
    selected: list[LensEvidenceBagItem] = []
    selected_nodes: list[_WorkingNode] = []
    used_chars = 0

    for node in ranked:
        if len(selected) >= max_items or used_chars >= char_budget:
            break
        content = _packed_content(node.obj)
        base_density = _density(node.score, len(content))
        adjusted_density = base_density * (1.0 - _redundancy_penalty(node, selected_nodes))
        remaining_space = char_budget - used_chars
        if remaining_space <= 0:
            break

        packed_content = content
        is_truncated = False
        if len(packed_content) > remaining_space:
            if remaining_space < 120:
                continue
            packed_content = packed_content[:remaining_space].rstrip()
            is_truncated = True

        item = LensEvidenceBagItem(
            semantic_id=node.obj.semantic_id,
            source_ref=_source_ref(node.obj),
            kind=node.obj.kind,
            heading_trail=_heading_trail(node.obj),
            depth=node.depth,
            source_role=_source_role(node.obj.semantic_id, node.depth, seed_ids),
            content=packed_content,
            score=node.score,
            density=adjusted_density,
            is_truncated=is_truncated,
            score_components=dict(node.score_components or {}),
        )
        selected.append(item)
        selected_nodes.append(node)
        used_chars += item.weight

    return selected


def _candidate_text(obj: SemanticObject) -> str:
    occurrence = obj.occurrence
    source_ref = occurrence.source_ref if occurrence else ""
    heading_trail = " > ".join(str(item) for item in occurrence.local_context.get("heading_trail", ())) if occurrence else ""
    return "\n".join(part for part in (source_ref, heading_trail, obj.kind, obj.content) if part)


def _semantic_structured_text(obj: SemanticObject) -> str:
    occurrence = obj.occurrence
    source_ref = occurrence.source_ref if occurrence else ""
    heading_trail = tuple(str(item) for item in occurrence.local_context.get("heading_trail", ())) if occurrence else ()
    heading_text = " > ".join(heading_trail)
    kind = obj.kind
    preview = _preview(obj.content, limit=500)
    structural = obj.surfaces.structural
    block_index = structural.get("block_index")
    parts = [
        f"source: {source_ref}",
        f"heading: {heading_text}",
        f"kind: {kind}",
        f"block_index: {block_index}",
        f"content: {preview}",
    ]
    return "\n".join(part for part in parts if part and part != "block_index: None")


def _exact_match_score(query: str, obj: SemanticObject) -> float:
    query_lower = query.lower().strip()
    if not query_lower:
        return 0.0
    heading_text = " ".join(_heading_trail(obj)).lower()
    content = obj.content.lower()
    source_ref = _source_ref(obj).lower()
    score = 0.0
    if query_lower in content:
        score += 1.0
    if query_lower in heading_text:
        score += 0.75
    if query_lower in source_ref:
        score += 0.25
    return score


def _tokenize_query(query: str) -> set[str]:
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(query)
        if len(token) >= 3 and token.lower() not in COMMON_STOPWORDS
    }


def _normalize(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    vmin = float(values.min())
    vmax = float(values.max())
    if math.isclose(vmin, vmax):
        if math.isclose(vmax, 0.0):
            return np.zeros_like(values, dtype=float)
        return np.ones_like(values, dtype=float)
    return (values - vmin) / (vmax - vmin)


def _preview(content: str, *, limit: int = 220) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


def _source_ref(obj: SemanticObject) -> str:
    if obj.occurrence:
        return obj.occurrence.source_ref
    if obj.provenance:
        return obj.provenance[0].source_ref
    return ""


def _heading_trail(obj: SemanticObject) -> tuple[str, ...]:
    if obj.occurrence:
        trail = obj.occurrence.local_context.get("heading_trail", ())
        return tuple(str(item) for item in trail)
    value = obj.surfaces.structural.get("heading_trail", ())
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _relation_count(obj: SemanticObject, graph_edges: list[_GraphEdge]) -> int:
    semantic_id = obj.semantic_id
    return sum(1 for edge in graph_edges if edge.from_id == semantic_id or edge.to_id == semantic_id)


def _packed_content(obj: SemanticObject) -> str:
    heading_text = " > ".join(_heading_trail(obj))
    source_ref = _source_ref(obj)
    lines = []
    if source_ref:
        lines.append(f"source: {source_ref}")
    if heading_text:
        lines.append(f"heading: {heading_text}")
    lines.append(obj.content.strip())
    return "\n".join(part for part in lines if part)


def _density(score: float, content_len: int, *, alpha: float = 1.08, base_cost: float = 100.0) -> float:
    weight = math.pow(max(content_len, 1), alpha) + base_cost
    return score / weight


def _redundancy_penalty(node: _WorkingNode, selected: list[_WorkingNode]) -> float:
    if not selected:
        return 0.0
    penalty = 0.0
    source_ref = _source_ref(node.obj)
    heading = set(item.lower() for item in _heading_trail(node.obj))
    for prior in selected:
        prior_source = _source_ref(prior.obj)
        if source_ref and source_ref == prior_source:
            penalty += 0.30
        prior_heading = set(item.lower() for item in _heading_trail(prior.obj))
        if heading and prior_heading:
            penalty += 0.20 * (len(heading & prior_heading) / len(heading))
        if node.obj.kind == prior.obj.kind and source_ref and source_ref == prior_source:
            penalty += 0.25
    return min(penalty, 0.75)


def _source_role(semantic_id: str, depth: int, seed_ids: set[str]) -> str:
    if semantic_id in seed_ids:
        return "seed"
    if depth <= 1:
        return "neighbor"
    return "propagated"
