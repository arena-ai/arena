import { Flex, Text, useToast } from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';
import { DocumentsService, Document } from '@app/client'

const FileUploadDropzone = ({onUpload: onUpload}: {onUpload: (document: Document) => void}) => {
  const toast = useToast();

  const { getRootProps, getInputProps } = useDropzone({
      onDrop: (files) => {
        // Handle dropped files here
        const formData = new FormData();
        files.forEach((file) => {
          formData.append('file', file);
        });
        const blob = formData.get('file');
        DocumentsService.createFile({formData: {upload: blob as Blob}}).then(
          (document) => {
            onUpload(document);
            toast({
              title: "Upload successful.",
              description: `Uploaded ${document.filename} file(s) successfully.`,
              status: "success",
              duration: 3000,
              isClosable: true,
            });
          },
          (reason) => {
            toast({
              title: "Upload failed.",
              description: reason,
              status: "error",
              duration: 3000,
              isClosable: true,
            });
          },
        );
      },
    });

  return (
    <Flex
      {...getRootProps({
        className: 'dropzone',
      })}
      p={4}
      borderWidth={1}
      textColor="gray.400"
      borderColor="gray.400"
      borderRadius="xl"
      cursor="pointer"
      alignItems='center'
      maxW={600}
      h={200}
    >
      <input {...getInputProps()} />
      <Text w="100%" textAlign="center">Drag 'n' drop files here, or click to select files</Text>
    </Flex>
  );
};

export default FileUploadDropzone;