"""Unit tests for organization tree service."""

from modules.organization.service.org_tree_service import OrgTreeService


def test_build_dept_tree_nested() -> None:
    flat: list[dict[str, object]] = [
        {"id": "1", "code": "FIN", "name": "Finance", "parent_id": None, "children": []},
        {"id": "2", "code": "AP", "name": "AP", "parent_id": "1", "children": []},
    ]
    roots = OrgTreeService._build_dept_tree(flat)
    assert len(roots) == 1
    assert roots[0]["code"] == "FIN"
    assert len(roots[0]["children"]) == 1
    assert roots[0]["children"][0]["code"] == "AP"
