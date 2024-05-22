import { Button } from '@chakra-ui/react';
import { EventsService } from '@app/client'


const DownloadButton = () => {
  const downloadFile = async () => {
    try {
      const response = await EventsService.downloadEvents({format: "arrow"});

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'arena.arrow'); //or any other extension
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