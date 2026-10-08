/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DataTable, type DataTableColumn } from "@/components/shared/data-table";

type Row = { id: string; name: string; amount: number };

const ROWS: Row[] = [
  { id: "1", name: "Charlie", amount: 30 },
  { id: "2", name: "Alpha", amount: 10 },
  { id: "3", name: "Bravo", amount: 20 },
];

const COLUMNS: DataTableColumn<Row>[] = [
  { key: "name", header: "Name", cell: (r) => r.name, sortValue: (r) => r.name },
  {
    key: "amount",
    header: "Amount",
    cell: (r) => r.amount,
    sortValue: (r) => r.amount,
    align: "right",
  },
];

function bodyNames() {
  const rows = screen.getAllByRole("row").slice(1);
  return rows.map((row) => within(row).getAllByRole("cell")[0]?.textContent);
}

afterEach(() => {
  cleanup();
});

describe("DataTable", () => {
  it("sorts by a column and toggles direction", async () => {
    const user = userEvent.setup();
    render(<DataTable columns={COLUMNS} rows={ROWS} getRowId={(r) => r.id} />);
    expect(bodyNames()).toEqual(["Charlie", "Alpha", "Bravo"]);

    await user.click(screen.getByRole("button", { name: /Name/ }));
    expect(bodyNames()).toEqual(["Alpha", "Bravo", "Charlie"]);

    await user.click(screen.getByRole("button", { name: /Name/ }));
    expect(bodyNames()).toEqual(["Charlie", "Bravo", "Alpha"]);
  });

  it("filters rows with the toolbar search and shows a no-results state", async () => {
    const user = userEvent.setup();
    render(
      <DataTable
        title="Accounts"
        columns={COLUMNS}
        rows={ROWS}
        getRowId={(r) => r.id}
        searchPlaceholder="Search accounts"
      />,
    );
    await user.type(screen.getByRole("searchbox", { name: "Search accounts" }), "bra");
    expect(bodyNames()).toEqual(["Bravo"]);

    await user.clear(screen.getByRole("searchbox", { name: "Search accounts" }));
    await user.type(screen.getByRole("searchbox", { name: "Search accounts" }), "zzz");
    expect(screen.getByText("No results")).toBeInTheDocument();
  });

  it("paginates", async () => {
    const user = userEvent.setup();
    render(<DataTable columns={COLUMNS} rows={ROWS} getRowId={(r) => r.id} pageSize={2} />);
    expect(bodyNames()).toEqual(["Charlie", "Alpha"]);
    expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Next page" }));
    expect(bodyNames()).toEqual(["Bravo"]);
  });

  it("selects rows and passes them to bulk actions", async () => {
    const user = userEvent.setup();
    const onArchive = vi.fn();
    render(
      <DataTable
        columns={COLUMNS}
        rows={ROWS}
        getRowId={(r) => r.id}
        selectable
        bulkActions={(selected) => (
          <button type="button" onClick={() => onArchive(selected.map((r) => r.id))}>
            Archive
          </button>
        )}
      />,
    );
    await user.click(screen.getByRole("checkbox", { name: "Select row 1" }));
    await user.click(screen.getByRole("checkbox", { name: "Select row 3" }));
    expect(screen.getByText("2 selected")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Archive" }));
    expect(onArchive).toHaveBeenCalledWith(["1", "3"]);

    await user.click(screen.getByRole("button", { name: "Clear selection" }));
    expect(screen.queryByText("2 selected")).not.toBeInTheDocument();
  });

  it("renders the error state with retry instead of rows", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(
      <DataTable
        columns={COLUMNS}
        rows={ROWS}
        getRowId={(r) => r.id}
        error="Network down"
        onRetry={onRetry}
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Network down");
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalled();
  });

  it("shows the empty state when there are no rows", () => {
    render(<DataTable columns={COLUMNS} rows={[]} getRowId={(r) => r.id} />);
    expect(screen.getByText("No records yet")).toBeInTheDocument();
  });
});
