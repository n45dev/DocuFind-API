const API_URL = "http://localhost:5000"; // Flask API server

document
  .getElementById("uploadForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const pdfFile = document.getElementById("pdfFile").files[0];
    if (!pdfFile) {
      alert("Please select a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file", pdfFile);
    formData.append("key", "stop_hacking_srinath"); // Add the key for authorization

    const response = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    console.log(data); // Log the response for debugging
    if (response.ok) {
      displayResults(data); // Pass the response data to display the underlined PDF and images
    } else {
      alert("Error processing PDF: " + data.error);
    }
  });

function displayResults(data) {
  const {
    extracted_aadhaar_numbers,
    extracted_pan_numbers,
    extracted_dl_numbers,
    extracted_phone_numbers,
    no_of_pages,
    pdf_id,
  } = data;

  document.getElementById("aadhaarNumbers").innerHTML =
    `<strong>Aadhaar Numbers:</strong> ${extracted_aadhaar_numbers.join(", ")}`;
  document.getElementById("panNumbers").innerHTML =
    `<strong>PAN Numbers:</strong> ${extracted_pan_numbers.join(", ")}`;
  document.getElementById("dlNumbers").innerHTML =
    `<strong>DL Numbers:</strong> ${extracted_dl_numbers.join(", ")}`;
  document.getElementById("phoneNumbers").innerHTML =
    `<strong>Phone Numbers:</strong> ${extracted_phone_numbers.join(", ")}`;

  // Link to download the underlined PDF
  const downloadLink = document.createElement("a");
  downloadLink.href = `${API_URL}/pdf/${pdf_id}?key=stop_hacking_srinath`; // Fetch the underlined PDF using the key
  downloadLink.textContent = "Download Underlined PDF";
  downloadLink.download = "underlined.pdf"; // Name for the downloaded PDF
  document.getElementById("downloadLink").innerHTML = ""; // Clear any previous content
  document.getElementById("downloadLink").appendChild(downloadLink);

  // For displaying the images of the underlined PDF pages
  const imageContainer = document.getElementById("imageContainer");
  imageContainer.innerHTML = ""; // Clear previous images

  for (let page = 1; page <= no_of_pages; page++) {
    const img = document.createElement("img");
    img.src = `${API_URL}/image/${pdf_id}/${page}?key=stop_hacking_srinath`; // Fetch the underlined image for each page
    img.alt = `Page ${page}`;
    img.style.width = "100%"; // Resize for web display
    imageContainer.appendChild(img);
  }

  document.getElementById("results").style.display = "block"; // Show the results section
}
