const form = document.querySelector("form");
const fileInput = form.querySelector(".file-input");

form.addEventListener("click", () =>{
    fileInput.click();
    showfile()
});

let filepath =[]

fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/display-file', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const files = await response.json();
            const filesDiv = document.getElementById('files');
            filesDiv.innerHTML = '';

            files.forEach(file => {
                const uploaded = document.createElement('div');
                uploaded.classList.add('uploaded');
                uploaded.innerHTML = `
                    <li class="row">
                        <div class="content">
                            <i class='bx bxs-file'></i>
                            <div class="details">
                                <span class="name">${file.name} • Uploaded</span>
                                <span class="size">${file.size}</span>
                            </div>
                        </div>
                        <i class='bx bx-check'></i>
                    </li>`;
                    filepath.push(file.path)
                filesDiv.append(uploaded);
            });
        } else {
            console.error('Failed to upload file:', await response.json());
        }
    } else {
        console.error('No file selected.');
    }
});

async function get_notes(){
    query = filepath[0]

    const response = await fetch('/generate_audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(query)
    })

    const notes = await response.json();
}




