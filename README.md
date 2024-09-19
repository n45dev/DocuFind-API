# Smart India Hackathon Pre Project

> Note: This project was created as a part of the Smart India Hackathon Pre Project. The project was created in a span of 2 weeks.

## Problem Statement
Creating an application to identify the presence of government issued personally identifiable information (PII) embedded in documents and data, inadvertently or otherwise.

## Team Members
1. Samyak Sanganeria
2. [Naga Srinath](https://knsrinath.com)
3. Shinde Kaushik
4. Himagiri Nandhan
5. Shashikanth
6. Chaitanya Medaboina

## To Do:
- [ ] Add all endpoints in README.md
- [ ] Secure the API
- [ ] Add error handling
- [ ] Use proper endpoint names

## Instructions to use the API server

### API Endpoints:

#### Base URL: `https://sih-api.knsrinath.com`
> Note: The API server is no longer running. You can run the server locally.

##### POST:

1. `/upload_pdf` - To upload a pdf file to the server
2. `/upload_text` - To upload a text to the server
3. `/upload_image` - To upload an image to the server

##### GET:

1. `/pdf/<file_id>` - To get the highlighted pdf file
2. `/image/<file_id>/<page_number>` - To get the highlighted image of a page in the pdf file
3. `/pdf_count` - To get the number of pdf files uploaded

### Example: Uploading a pdf to the API server

#### Using curl:

```bash
curl -X POST -F "file=@example_input.pdf" -F "key=stop_hacking_srinath" https://sih-api.knsrinath.com/upload
```

#### Java Script:

```javascript
const formData = new FormData();
formData.append("file", pdfFile);
formData.append("key", "stop_hacking_srinath");

const response = await fetch(`${API_URL}/upload`, {
  method: "POST",
  body: formData,
});
```
