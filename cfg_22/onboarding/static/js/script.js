document.addEventListener('DOMContentLoaded', function() {
    // Function to update file input labels
    function updateFileName(event) {
        // Get the file input element
        const fileInput = event.target;
        
        // Get the corresponding message element
        let messageElementId = fileInput.id === 'top_view' ? 'msg1' : 'msg2';
        const messageElement = document.getElementById(messageElementId);
        
        // Check if a file was selected
        if (fileInput.files.length > 0) {
            // Update the message to the selected file name
            messageElement.textContent = fileInput.files[0].name;
        } else {
            // Reset the message if no file is selected
            messageElement.textContent = 'No file chosen';
        }
    }

    // Attach the updateFileName function to file input elements
    function onFileChange() {
        // Get all file inputs
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(fileInput => {
            fileInput.addEventListener('change', updateFileName);
        });
    }

    // Initialize the file change event listener
    onFileChange();
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('areaForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(form); // Create a FormData object from the form

        fetch('/save_data', { // Update this URL to your API endpoint
            method: 'POST',
            body: formData
        })
        .then(response => response.json()) // Parse JSON response
        .then(data => {
            console.log(data);
            if (data.success) {
                console.log("hello");
                setTimeout(() => {
                    window.location.href = '/cost_analysis';
                  },2000);
                  console.log("hello");
                alert(data.message);  // Alert the message (Lantana decrease/increase)
                if ('change' in data) {
                    alert('Lantana change amount: ' + data.change);  // Alert the change amount if present
                }
                 // Redirect to the desired page
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error submitting the form.');
        });
    })
})