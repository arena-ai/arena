import { Button } from '@chakra-ui/react';
import { EventsService } from '@app/client'


const DownloadButton = ({ format: format }: { format: 'parquet' | 'csv' }) => {
  const downloadFile = async () => {
    try {
      const response = await EventsService.downloadEvents({ format: format })
      console.log(response)
      const url = window.URL.createObjectURL(new Blob([response], { type: format === 'parquet' ? "application/octet-stream" : "" }))
      console.log(url)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `arena.${format}`) //or any other extension
      document.body.appendChild(link)
      link.click()
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