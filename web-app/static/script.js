// Demo angle data 
// const demoAngles = {
//   "Thumb MCP→IP": 161.44,
//   "Thumb IP→Tip": 133.85,
//   "Index MCP→PIP": 152.81,
//   "Index PIP→DIP": 70.18,
//   "Middle MCP→PIP": 148.49,
//   "Middle PIP→DIP": 69.31,
//   "Ring MCP→PIP": 168.76,
//   "Ring PIP→DIP": 40.95,
//   "Pinky MCP→PIP": 177.22,
//   "Pinky PIP→DIP": 47.28
// };

// Fill form with demo data for testing
async function getLiveAngles(formType) {
  const tableId = formType === 'reg' ? 'hand-angles-table-reg' : 'hand-angles-table-login';

  try {
    const response = await fetch("http://localhost:5050/hand-angles");
    if (!response.ok) throw new Error("Failed to fetch angles");
    const angleArray = await response.json();

    const labels = [
      "Thumb MCP→IP", "Thumb IP→Tip",
      "Index MCP→PIP", "Index PIP→DIP",
      "Middle MCP→PIP", "Middle PIP→DIP",
      "Ring MCP→PIP", "Ring PIP→DIP",
      "Pinky MCP→PIP", "Pinky PIP→DIP"
    ];

    // Fill inputs based on labels
    const inputs = document.querySelectorAll(`#${tableId} input`);
    inputs.forEach(input => {
      const label = input.getAttribute('data-angle');
      const index = labels.indexOf(label);
      if (index !== -1 && angleArray[index] !== undefined) {
        input.value = angleArray[index].toFixed(2);
      }
    });

    document.getElementById("result").textContent = "✅ Hand angles updated from live feed!";
  } catch (err) {
    console.error("Error fetching hand angles:", err);
    document.getElementById("result").textContent = "❌ Could not fetch live hand data.";
  }
}


function collectAngleData(tableId) {
  const inputs = document.querySelectorAll(`#${tableId} input`);
  const angleData = {};

  inputs.forEach(input => {
    const angleName = input.getAttribute('data-angle');
    const value = input.value.trim();

    if (!value) {
      throw new Error(`Missing value for ${angleName}`);
    }

    const floatVal = parseFloat(value);
    if (isNaN(floatVal)) {
      throw new Error(`Invalid number for ${angleName}`);
    }

    angleData[angleName] = floatVal;
  });

  return angleData;
}

async function submitRegister() {
  const username = document.getElementById("reg-username").value.trim();
  const gesture_name = document.getElementById("reg-gesture").value.trim();
  const resultEl = document.getElementById("result");

  if (!username || !gesture_name) {
    resultEl.textContent = "Please fill in all required fields.";
    return;
  }

  let angle_data;
  try {
    angle_data = collectAngleData("hand-angles-table-reg");
  } catch (err) {
    resultEl.textContent = err.message;
    return;
  }

  const res = await fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username,
      gesture_name,
      angle_data
    })
  });

  const data = await res.json();
  resultEl.textContent = res.ok
    ? `Registered! Gesture ID: ${data.gesture_password_id}`
    : `Error: ${data.error}`;
}

async function submitLogin() {
  const username = document.getElementById("login-username").value.trim();
  const resultEl = document.getElementById("result");

  if (!username) {
    resultEl.textContent = "Username is required.";
    return;
  }

  let angle_data;
  try {
    angle_data = collectAngleData("hand-angles-table-login");
  } catch (err) {
    resultEl.textContent = err.message;
    return;
  }

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username,
      angle_data
    })
  });

  const data = await res.json();
  
  if (res.ok) {
    resultEl.textContent = data.message + (data.confidence ? ` (Confidence: ${data.confidence.toFixed(2)})` : "");
    
    // Load documents
    loadDocuments(username);
  } else {
    resultEl.textContent = `Error: ${data.error}`;
  }
}

async function loadDocuments(username) {
  const res = await fetch(`/documents?username=${username}`);
  if (res.ok) {
    const data = await res.json();
    const docListEl = document.getElementById("doc-list");
    docListEl.innerHTML = "";
    
    if (data.documents.length === 0) {
      docListEl.innerHTML = "<p>No documents found. Create a new one!</p>";
    } else {
      data.documents.forEach(doc => {
        const docEl = document.createElement("div");
        docEl.className = "document-item";
        docEl.innerHTML = `
          <h3>${doc.title}</h3>
          <p>Last updated: ${new Date(doc.updated_at).toLocaleString()}</p>
          <button onclick="openDocument('${doc.id}', '${username}')">Open</button>
        `;
        docListEl.appendChild(docEl);
      });
    }
    
    document.getElementById("document-section").style.display = "block";
  }
}

let currentDocId = null;
let currentUsername = null;

async function openDocument(docId, username) {
  const res = await fetch(`/documents/${docId}?username=${username}`);
  if (res.ok) {
    const doc = await res.json();
    document.getElementById("doc-title").value = doc.title;
    document.getElementById("doc-content").value = doc.content;
    document.getElementById("editor").style.display = "block";
    
    currentDocId = docId;
    currentUsername = username;
  }
}

function closeEditor() {
  document.getElementById("editor").style.display = "none";
  currentDocId = null;
}

async function saveDocument() {
  if (!currentDocId || !currentUsername) return;
  
  const content = document.getElementById("doc-content").value;
  
  const res = await fetch(`/documents/${currentDocId}?username=${currentUsername}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content })
  });
  
  if (res.ok) {
    alert("Document saved successfully!");
    loadDocuments(currentUsername);
  } else {
    alert("Error saving document");
  }
}

async function createNewDocument() {
  const username = document.getElementById("login-username").value.trim();
  if (!username) return;
  
  const title = prompt("Enter document title:");
  if (!title) return;
  
  // Create a new document for the user
  const res = await fetch(`/documents?username=${username}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: title,
      content: ""
    })
  });
  
  if (res.ok) {
    const data = await res.json();
    alert(`New document "${title}" created successfully!`);
    loadDocuments(username);
    
    // Open the new document
    if (data.document_id) {
      openDocument(data.document_id, username);
    }
  } else {
    alert("Error creating document");
  }
}