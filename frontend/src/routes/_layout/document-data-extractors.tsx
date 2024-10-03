import { useState, MouseEventHandler } from 'react'
import {
  Container,
  Flex,
  Box,
  Heading,
  Spinner,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  Input,
  Textarea,
  Select,
  Tag,
  Text,
  useColorModeValue,
  Button,
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useQueryClient, useQuery } from '@tanstack/react-query'

import { ApiError, DocumentsService, DocumentDataExtractorsService, DocumentDataExtractorOut } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'

export const Route = createFileRoute('/_layout/document-data-extractors')({
  component: DocumentDataExtractors,
})

function ExtractorExamples({documentDataExtractor, is_selected, onClick}: {documentDataExtractor: DocumentDataExtractorOut, is_selected: boolean, onClick: MouseEventHandler}) {
  // Pull document data examples
  const [documentId, setDocumentId] = useState("");
  const [data, setData] = useState("");
  const showToast = useCustomToast()
  const secBgColor = useColorModeValue('ui.secondary', 'ui.darkSlate')
  const queryClient = useQueryClient()
  // Pull documents
  const {
    data: documents,
    isError,
    error,
  } = useQuery({
    queryKey: ['documents'],
    queryFn: () => DocumentsService.readFiles(),
  })

  if (isError) {
    const errDetail = (error as ApiError).body?.detail
    showToast('Something went wrong.', `${errDetail}`, 'error')
  }

  return (
    (is_selected ?
      <>
        <Thead>
          <Tr bgColor={secBgColor}>
            <Th>Name</Th>
            <Th>Prompt</Th>
            <Th>Timestamp</Th>
            <Th></Th>
          </Tr>
        </Thead>
        <Tbody onClick={onClick}>
          <Tr key={documentDataExtractor.name} bgColor={secBgColor}>
            <Td><Tag bgColor="teal">{documentDataExtractor.name}</Tag></Td>
            <Td><Text whiteSpace="pre">{documentDataExtractor.prompt}</Text></Td>
            <Td>{documentDataExtractor.timestamp}</Td>
            <Td></Td>
          </Tr>
        </Tbody>
        <Thead>
          <Tr bgColor={secBgColor}>
            <Th>Examples</Th>
            <Th>Document</Th>
            <Th>Data</Th>
            <Th></Th>
          </Tr>
        </Thead>
        <Tbody>
          <Tr bgColor={secBgColor}>
            <Td></Td>
            <Td>
              <Select placeholder="Select Document"
                onChange={(e)=>setDocumentId(e.target.value)}
              >
                {documents?.data.map((document) => (
                  <option value={document.name}>{document.filename}</option>
                ))}
              </Select>
            </Td>
            <Td>
              <Textarea placeholder="Data to Extract"
                onChange={(e)=>setData(e.target.value)}
              />
            </Td>
            <Td><Button colorScheme='teal' onClick={()=>{
                DocumentDataExtractorsService.createDocumentDataExample({
                  name: documentDataExtractor.name,
                  requestBody: {document_id: documentId, data: data, document_data_extractor_id: documentDataExtractor.id}
                }).then(()=> queryClient.invalidateQueries({ queryKey: ['document_data_extractors'] }));
              }}>Add Example</Button>
            </Td>
          </Tr>
        </Tbody>
        <Tbody>
          {documentDataExtractor.document_data_examples.map((documentDataExample) => (
            <Tr key={documentDataExample.id} bgColor={secBgColor}>
              <Td></Td>
              <Td>{documentDataExample.document_id}</Td>
              <Td><Text whiteSpace="pre">{documentDataExample.data}</Text></Td>
              <Td></Td>
            </Tr>
          ))}
        </Tbody>
      </>
      :
      <>
        <Tbody onClick={onClick}>
          <Tr key={documentDataExtractor.name}>
            <Td><Tag>{documentDataExtractor.name}</Tag></Td>
            <Td><Text whiteSpace="pre">{documentDataExtractor.prompt}</Text></Td>
            <Td>{documentDataExtractor.timestamp}</Td>
            <Td></Td>
          </Tr>
        </Tbody>
      </>
    )
  )
}

function DataExtractors() {
  const [selectedExtractor, selectExtractor] = useState("");
  const [name, setName] = useState("");
  const [prompt, setPrompt] = useState("");
  const showToast = useCustomToast()
  // Pull document data extractors
  const {
    data: documentDataExtractors,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['document_data_extractors'],
    queryFn: () => DocumentDataExtractorsService.readDocumentDataExtractors({}),
  })
  const queryClient = useQueryClient()
  
  if (isError) {
    const errDetail = (error as ApiError).body?.detail
    showToast('Something went wrong.', `${errDetail}`, 'error')
  }

  return (
    <>
      {isLoading ? (
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        documentDataExtractors && (            
        <Box py={4}>
          <Heading size='sm'>Data Extractors</Heading>
          <TableContainer py={4}>
            <Table size={{ base: 'sm', md: 'md' }} whiteSpace="normal">
              <Thead>
                <Tr>
                  <Th>Name</Th>
                  <Th>Prompt</Th>
                  <Th>Timestamp</Th>
                  <Th></Th>
                </Tr>
              </Thead>
              <Tbody>
                <Tr>
                  <Td>
                    <Input placeholder="Extractor Name"
                      onChange={(e)=>setName(e.target.value)}
                    />
                  </Td>
                  <Td>
                    <Textarea placeholder="Prompt"
                      onChange={(e)=>setPrompt(e.target.value)}
                    />
                  </Td>
                  <Td></Td>
                  <Td><Button colorScheme='teal' onClick={()=>{
                      DocumentDataExtractorsService.createDocumentDataExtractor({
                        requestBody: {name: name, prompt: prompt}
                      }).then(()=> queryClient.invalidateQueries({ queryKey: ['document_data_extractors'] }));
                    }}>Add Extractor</Button>
                  </Td>
                </Tr>
              </Tbody>
              {documentDataExtractors.data.map((documentDataExtractor) => (
                <ExtractorExamples
                  documentDataExtractor={documentDataExtractor}
                  is_selected={documentDataExtractor.name===selectedExtractor}
                  onClick={()=>{selectExtractor(documentDataExtractor.name)}}/>
              ))}
            </Table>
          </TableContainer>
        </Box>
        )
      )}
    </>
  )
}

function DocumentDataExtractors() {
  const showToast = useCustomToast()

  // Pull documents
  const {
    data: documents,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['documents'],
    queryFn: () => DocumentsService.readFiles(),
  })
  
  if (isError) {
    const errDetail = (error as ApiError).body?.detail
    showToast('Something went wrong.', `${errDetail}`, 'error')
  }

  return (
    <>
      {isLoading ? (
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        documents && (            
          <Container maxW="full">
            <Heading
              size="lg"
              textAlign={{ base: 'center', md: 'left' }}
              pt={12}
            >
              Document Data Extractors
            </Heading>
            <DataExtractors />
          </Container>
        )
      )}
    </>
  )
}

export default DocumentDataExtractors
