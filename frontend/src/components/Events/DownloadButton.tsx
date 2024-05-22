import { Button } from '@chakra-ui/react';
import { EventsService } from '@app/client'
import axios from 'axios';

const DownloadButton = ({ format: format }: { format: 'parquet' | 'csv' }) => {
  const downloadFile = async () => {
    try {
      axios.defaults.responseType = 'blob'
      // @ts-expect-error: It's a hack
      const response: Blob = await EventsService.downloadEvents({ format: format })
      const url = window.URL.createObjectURL(response)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `arena.${format}`) //or any other extension
      document.body.appendChild(link)
      link.click()
      axios.defaults.responseType = undefined
    } catch (error) {
      console.error('Download Error:', error)
    }
  };

  return (
    <Button colorScheme="teal" onClick={downloadFile}>
      {`Download ${format}`}
    </Button>
  );
};

export default DownloadButton;