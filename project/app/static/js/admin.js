async function doExport(e) {
    e.preventDefault();

    const id = document.getElementById("exportId").value.trim();

    if (!id) {
        alert("enter participant id");
        return;
    }

    const token = prompt("Enter admin token (will not be saved)");

    if (!token) {
        return;
    }

    const res = await fetch(
        "/export/" + encodeURIComponent(id),
        {
            headers: {
                "X-ADMIN-TOKEN": token
            }
        }
    );

    const json = await res.json();

    if (json.ok && json.records) {
        const blob = new Blob(
            [JSON.stringify(json, null, 2)],
            { type: "application/json" }
        );

        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `export-${id}.json`;
        a.click();

        URL.revokeObjectURL(a.href);
    } else {
        alert(
            "Export failed: " +
            (json.error || JSON.stringify(json))
        );
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const exportForm = document.getElementById("exportForm");

    if (exportForm) {
        exportForm.addEventListener("submit", doExport);
    }
});
