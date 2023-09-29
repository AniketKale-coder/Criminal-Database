


const imageInput = document.getElementById('input-file');
const dragArea = document.getElementById('drop-area');
const imageContainer = document.getElementById('uploadContainer');

imageInput.addEventListener("change", uploadImage);

function uploadImage() {
  const file = imageInput.files[0];

  if (file) {
    let imgLink = URL.createObjectURL(file);
    imageContainer.style.backgroundImage = `url(${imgLink})`;
    imageContainer.textContent = "";
  } else {
    imageContainer.style.backgroundImage = "";
    imageContainer.textContent = "Drag and drop file here! or click to upload.";
  }
}

dragArea.addEventListener("dragover", (e) => {
  e.preventDefault();
});

dragArea.addEventListener("drop", (e) => {
  e.preventDefault();
  imageInput.files = e.dataTransfer.files;
  uploadImage();
});

const rightContainer = document.querySelector('.right');
const nameElement = document.querySelector('.name');
const infoElement = document.querySelector('.info');
const resultImageElement = document.getElementById('resultedImage').querySelector('img');

// const uploadButton = document.getElementById('btn');
// uploadButton.addEventListener('click', sendImageToServer);

async function sendImageToServer() {
  const file = imageInput.files[0];

  if (file) {
    const formData = new FormData();
    formData.append('image', file);

    const UploadedImage = crypto.randomUUID();



      fetch(`https://ryufmqrr61.execute-api.us-east-1.amazonaws.com/dev/suspectesimages/${UploadedImage}.jpeg`, {
        method: 'PUT',
        headers: {
          'Content-Type' : 'image/jpeg'

        },
        body: formData,
      }).then(async()=>{
        const response = await authenticate(uploadImage);
        if(response == "Success")
        {
          console.log("success");
        }else{
          console.log("failed");
        }
      }).catch(e=>{
        console.error(e);
      })
    
    }
}

async function authenticate(UploadedImage){
  const requestUrl = 'https://ryufmqrr61.execute-api.us-east-1.amazonaws.com/dev/criminal?' + new URLSearchParams({
    objectKey: `${UploadedImage}.jpeg`
  });
  return await fetch(requestUrl,{
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    }
  }).then(res => res.json())
  .then((data) =>{
    return data;
  }).catch(error => console.error(error));
}

const loadingElement = document.querySelector('.loading');

async function handleResponse(responseData) {
  loadingElement.style.display = 'block';

  await new Promise(resolve => setTimeout(resolve, 1500));

  loadingElement.style.display = 'none';

  if (responseData.name && responseData.info && responseData.imageURL) {
    nameElement.textContent = `Name: ${responseData.name}`;
    infoElement.textContent = responseData.info;
    resultImageElement.src = responseData.imageURL;
    dragArea.style.display = 'none';
    rightContainer.style.display = 'block';
  } else {
    console.error('Invalid response data:', responseData);
  }
}
document.querySelector('form').addEventListener('submit', (event) => {
  event.preventDefault();
  sendImageToServer();
});