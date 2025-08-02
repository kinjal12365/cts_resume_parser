document.addEventListener("DOMContentLoaded", async () => {
    const tableBody = document.getElementById("tableBody");

    try {
        const response = await fetch("/list-files");
        const files = await response.json();

        if (!Array.isArray(files)) {
            tableBody.innerHTML = `<tr><td colspan="4">Error loading files</td></tr>`;
            return;
        }

        tableBody.innerHTML = "";

        files.forEach(file => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${file.name}</td>
                <td>${file.size}</td>
                <td>${file.last_modified}</td>
                <td><a href="${file.url}" target="_blank">View</a></td>
            `;

            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error(err);
        tableBody.innerHTML = `<tr><td colspan="4">Error fetching file list</td></tr>`;
    }
});
