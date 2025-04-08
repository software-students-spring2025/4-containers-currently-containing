
    function collectHandPositions(tableId) {
      const inputs = document.querySelectorAll(`#${tableId} input`);
      const joints = {};

      inputs.forEach(input => {
        const joint = input.getAttribute('data-joint');
        const axis = input.getAttribute('data-axis');
        const value = input.value.trim();

        if (!value) {
          throw new Error(`Missing ${axis.toUpperCase()} value for ${joint}`);
        }

        const floatVal = parseFloat(value);
        if (isNaN(floatVal)) {
          throw new Error(`Invalid number for ${joint} ${axis}`);
        }

        joints[joint] = joints[joint] || { joint_id: joint };
        joints[joint][axis] = floatVal;
      });

      return Object.values(joints);
    }


    async function submitRegister() {
      const username = document.getElementById("reg-username").value.trim();
      const gesture_name = document.getElementById("reg-gesture").value.trim();
      const resultEl = document.getElementById("result");

      if (!username || !gesture_name) {
        resultEl.textContent = "Please fill in all required fields.";
        return;
      }

      let hand_positions;
      try {
        hand_positions = collectHandPositions("hand-positions-table-reg");
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
          hand_positions
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

      let hand_positions;
      try {
        hand_positions = collectHandPositions("hand-positions-table-login");
      } catch (err) {
        resultEl.textContent = err.message;
        return;
      }

      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          gesture_data: hand_positions
        })
      });

      const data = await res.json();
      resultEl.textContent = res.ok
        ? data.message + (data.confidence ? ` (Confidence: ${data.confidence.toFixed(2)})` : "")
        : `Error: ${data.error}`;
    }

  