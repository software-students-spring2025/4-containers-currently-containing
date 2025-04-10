// Demo angle data 
const demoAngles = {
  "Thumb MCP→IP": 161.44,
  "Thumb IP→Tip": 133.85,
  "Index MCP→PIP": 152.81,
  "Index PIP→DIP": 70.18,
  "Middle MCP→PIP": 148.49,
  "Middle PIP→DIP": 69.31,
  "Ring MCP→PIP": 168.76,
  "Ring PIP→DIP": 40.95,
  "Pinky MCP→PIP": 177.22,
  "Pinky PIP→DIP": 47.28
};

async function getLiveAngles(formType) {
  const tableId = formType === 'reg' ? 'hand-angles-table-reg' : 'hand-angles-table-login';

  try {
    const response = await fetch("/api/hand-angles");
    const data = await response.json();

    if (!data.hand_present) {
      document.getElementById("result").textContent = "🖐️ Hand is not in view.";
      return;
    }

    const labels = [
      "Thumb MCP→IP", "Thumb IP→Tip",
      "Index MCP→PIP", "Index PIP→DIP",
      "Middle MCP→PIP", "Middle PIP→DIP",
      "Ring MCP→PIP", "Ring PIP→DIP",
      "Pinky MCP→PIP", "Pinky PIP→DIP"
    ];

    const inputs = document.querySelectorAll(`#${tableId} input`);
    inputs.forEach(input => {
      const label = input.getAttribute('data-angle');
      const index = labels.indexOf(label);
      const angle = data.angles[index];

      if (index !== -1 && angle !== null && angle !== undefined) {
        input.value = angle.toFixed(2);
      } else {
        input.value = ""; // Clear the input if no valid data
      }
    });

    document.getElementById("result").textContent = "✅ Hand angles updated!";
  } catch (err) {
    console.error("Error fetching hand angles:", err);
    document.getElementById("result").textContent = "❌ Could not connect to hand tracking system.";
  }
}

// Fill form with demo data for testing
function fillDemoData(formType) {
  const tableId = formType === 'reg' ? 'hand-angles-table-reg' : 'hand-angles-table-login';
  const inputs = document.querySelectorAll(`#${tableId} input`);
  
  inputs.forEach(input => {
    const angleName = input.getAttribute('data-angle');
    if (angleName in demoAngles) {
      input.value = demoAngles[angleName];
    }
  });
  
  if (formType === 'reg') {
    document.getElementById('reg-username').value = 'demo_angle_user';
    document.getElementById('reg-gesture').value = 'peace_sign';
  } else {
    document.getElementById('login-username').value = 'demo_angle_user';
  }
  
  document.getElementById("result").textContent = "✅ Demo data filled in!";
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

  try {
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
  } catch (err) {
    resultEl.textContent = `Network error: ${err.message}`;
    console.error("Registration error:", err);
  }
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

  try {
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
  } catch (err) {
    resultEl.textContent = `Network error: ${err.message}`;
    console.error("Login error:", err);
  }
}

async function loadDocuments(username) {
  try {
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
  } catch (err) {
    console.error("Error loading documents:", err);
    document.getElementById("result").textContent = `Error loading documents: ${err.message}`;
  }
}

let currentDocId = null;
let currentUsername = null;

async function openDocument(docId, username) {
  try {
    const res = await fetch(`/documents/${docId}?username=${username}`);
    if (res.ok) {
      const doc = await res.json();
      document.getElementById("doc-title").value = doc.title;
      document.getElementById("doc-content").value = doc.content;
      document.getElementById("editor").style.display = "block";
      
      currentDocId = docId;
      currentUsername = username;
    }
  } catch (err) {
    console.error("Error opening document:", err);
    document.getElementById("result").textContent = `Error opening document: ${err.message}`;
  }
}

function closeEditor() {
  document.getElementById("editor").style.display = "none";
  currentDocId = null;
}

async function saveDocument() {
  if (!currentDocId || !currentUsername) return;
  
  const content = document.getElementById("doc-content").value;
  
  try {
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
  } catch (err) {
    console.error("Error saving document:", err);
    alert(`Error saving document: ${err.message}`);
  }
}

async function createNewDocument() {
  const username = document.getElementById("login-username").value.trim();
  if (!username) return;
  
  const title = prompt("Enter document title:");
  if (!title) return;
  
  try {
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
  } catch (err) {
    console.error("Error creating document:", err);
    alert(`Error creating document: ${err.message}`);
  }
}