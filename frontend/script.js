const API = "http://localhost:8000";

let token = localStorage.getItem("token");
let currentNoteId = null;

const authScreen = document.getElementById("auth-screen");
const appScreen = document.getElementById("app-screen");

function showApp() {
    authScreen.classList.add("hidden");
    appScreen.classList.remove("hidden");
    loadNotes();
}

if (token) showApp();

/* AUTH */
async function login() {
    const email = emailInput.value;
    const password = passwordInput.value;

    const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("auth-msg").innerText = data.detail;
        return;
    }

    token = data.access_token;
    localStorage.setItem("token", token);
    showApp();
}

function logout() {
    localStorage.clear();
    location.reload();
}

/* NOTES */
async function loadNotes() {
    const res = await fetch(`${API}/notes`, {
        headers: { Authorization: `Bearer ${token}` }
    });

    const notes = await res.json();
    const list = document.getElementById("notes-list");
    list.innerHTML = "";

    notes.forEach(n => {
        const li = document.createElement("li");
        li.innerText = n.title;
        li.onclick = () => openNote(n);
        list.appendChild(li);
    });
}

function openNote(note) {
    currentNoteId = note.id;
    noteTitle.value = note.title;
    noteContent.value = note.content;
    loadComments();
}

function newNote() {
    currentNoteId = null;
    noteTitle.value = "";
    noteContent.value = "";
}

async function saveNote() {
    const payload = {
        title: noteTitle.value,
        content: noteContent.value
    };

    const url = currentNoteId
        ? `${API}/notes/${currentNoteId}`
        : `${API}/notes`;

    const method = currentNoteId ? "PUT" : "POST";

    await fetch(url, {
        method,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
    });

    loadNotes();
}

/* COMMENTS */
async function loadComments() {
    const res = await fetch(`${API}/comments/note/${currentNoteId}`);
    const comments = await res.json();

    const list = document.getElementById("comments-list");
    list.innerHTML = "";

    comments.forEach(c => {
        const li = document.createElement("li");
        li.innerText = c.content;
        list.appendChild(li);
    });
}

async function postComment() {
    const content = commentInput.value;

    await fetch(`${API}/comments`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            note_id: currentNoteId,
            content
        })
    });

    commentInput.value = "";
    loadComments();
}

/* VERSIONS */
async function loadVersions() {
    const panel = document.getElementById("versions-panel");
    panel.classList.remove("hidden");

    const res = await fetch(`${API}/notes/${currentNoteId}/versions`, {
        headers: { Authorization: `Bearer ${token}` }
    });

    const versions = await res.json();
    const list = document.getElementById("versions-list");
    list.innerHTML = "";

    versions.forEach(v => {
        const li = document.createElement("li");
        li.innerText = `Version ${v.version_number}`;
        list.appendChild(li);
    });
}

function closeVersions() {
    document.getElementById("versions-panel").classList.add("hidden");
}
