// script.js

const loader = document.getElementById('loader');
const resultDiv = document.getElementById('result');
const preview = document.getElementById('preview');

async function uploadImage() {
  const input = document.getElementById('imageInput');
  const file = input.files[0];

  if (!file) {
    alert('Please select an image.');
    return;
  }

  preview.src = URL.createObjectURL(file);
  preview.classList.remove("hidden");
  resultDiv.textContent = '';
  loader.classList.remove("hidden");

  const formData = new FormData();
  formData.append('image', file);

  try {
    const response = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    resultDiv.textContent = `✅ Result: ${data.result}`;
  } catch (err) {
    console.error(err);
    resultDiv.textContent = `❌ Error contacting backend.`;
  } finally {
    loader.classList.add("hidden");
  }
}
