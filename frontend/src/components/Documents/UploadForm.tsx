import {
  FileUploadDropzone,
  FileUploadList,
  FileUploadRoot,
} from '@chakra-ui/react';
import { DocumentsService } from '@app/client'
// import axios from 'axios';

const UploadForm = () => {

  // <form action="/files/" enctype="multipart/form-data" method="post">
  //   <input name="files" type="file" multiple>
  //   <input type="submit">
  //   </form>
  //   <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
  //   <input name="files" type="file" multiple>
  //   <input type="submit">
  //   </form>
  return (
    <FileUploadRoot maxW="xl" alignItems="stretch" maxFiles={10}>
      <FileUploadDropzone
        label="Drag and drop here to upload"
        description=".png, .jpg up to 5MB"
      />
      <FileUploadList />
    </FileUploadRoot>
  );
};

export default UploadForm;