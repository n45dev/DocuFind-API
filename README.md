# Smart India Hackathon Pre Project

## Problem Statement
Creating an application to identify the presence of government issued personally identifiable information (PII) embedded in documents and data, inadvertently or otherwise.

## Team Members
1. Samyak Sanganeria
2. [Naga Srinath](https://knsrinath.com)
3. Shinde Kaushik
4. Himagiri Nandhan
5. Shashikanth
6. Chaitanya Medaboina

## Instructions to use the API server

### API Endpoints:

#### Base URL: `https://sih-api.knsrinath.com`

##### POST:

1. `/upload` - To upload a file to the server

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
