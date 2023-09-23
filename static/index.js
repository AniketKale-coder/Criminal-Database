const imageInput = document.getElementById('input-file');
const dragArea = document.getElementById('drop-area');
const imageContainer = document.getElementById('uploadContainer');

imageInput.addEventListener("change", uploadImage)

function uploadImage() {
  const file = imageInput.files[0];

  if (file) {
    let imgLink = URL.createObjectURL(file);
    imageContainer.style.backgroundImage = `url(${imgLink})`;
    imageContainer.textContent = "";
  } else {
    // Handle the case when no image is selected
    imageContainer.style.backgroundImage = "";
    imageContainer.textContent = "Drag and drop file here! or click to upload.";
  }
}

dragArea.addEventListener("dragover", (e) => {
  e.preventDefault();
}
)
dragArea.addEventListener("drop", (e) => {
  e.preventDefault();
  imageInput.files = e.dataTransfer.files;
  uploadImage();
}
)





const rightContainer = document.querySelector('.right');
const nameElement = document.querySelector('.name');
const infoElement = document.querySelector('.info');
const resultImageElement = document.getElementById('resultedImage').querySelector('img');


const uploadButton = document.getElementById('btn');
uploadButton.addEventListener('click', sendImageToServer);


async function sendImageToServer() {
    const file = imageInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('YOUR_AWS_API_ENDPOINT_URL', {
                method: 'POST',
                body: formData
            });

            const responseData = await response.json();

      
            handleResponse(responseData);
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    } else {
        console.error('No image selected.');
    }
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

        // Hide the drag and drop area and show the right container
        dragArea.style.display = 'none';
        rightContainer.style.display = 'block';
    } else {
        // Handle the case where the response data is incomplete or unexpected
        console.error('Invalid response data:', responseData);
    }
}

