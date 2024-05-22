import { Button } from '@chakra-ui/react';
import { ApiError, EventsService } from '@app/client'


const DownloadButton = () => {
  const downloadFile = async () => {
    try {
      const response = await axios.get('YOUR_API_URL', {
        responseType: 'blob', // Important
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'file.pdf'); //or any other extension
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Download Error:', error);
    }
  };

  return (
    <Button colorScheme="teal" onClick={downloadFile}>
      Download File
    </Button>
  );
};

export default DownloadButton;