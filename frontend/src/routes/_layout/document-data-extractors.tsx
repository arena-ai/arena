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
  Text,
  Code,
  useColorModeValue,
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useQueries } from '@tanstack/react-query'

import { ApiError, DocumentsService, Document, DocumentDataExtractorsService, DocumentDataExtractorOut, DocumentDataExtractorsOut } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'

export const Route = createFileRoute('/_layout/document-data-extractors')({
  component: DocumentDataExtractors,
})

function ExtractorExamples({documentDataExtractor: documentDataExtractor, is_selected: is_selected}: {documentDataExtractor: DocumentDataExtractorOut, is_selected: boolean}) {
  const showToast = useCustomToast()
  // Pull document data examples
  const secBgColor = useColorModeValue('ui.secondary', 'ui.darkSlate')

  return (
    (is_selected ?
      <>
        <Tbody>
          <Tr key={documentDataExtractor.name} bgColor={secBgColor}>
            <Td w={32}><Code>{documentDataExtractor.name}</Code></Td>
            <Td w={32}>{documentDataExtractor.prompt}</Td>
            <Td w={32}>{documentDataExtractor.timestamp}</Td>
          </Tr>
        </Tbody>
        <Thead>
          <Tr bgColor={secBgColor} opacity={0.5}>
            <Th></Th>
            <Th>Name</Th>
            <Th>Data</Th>
          </Tr>
        </Thead>
        <Tbody>
          {documentDataExtractor.document_data_examples.map((documentDataExample) => (
            <Tr key={documentDataExample.id} bgColor={secBgColor} opacity={0.5}>
              <Td w={32}></Td>
              <Td w={32}>{documentDataExample.document_id}</Td>
              <Td w={32}>{documentDataExample.data}</Td>
            </Tr>
          ))}
        </Tbody>
      </>
      :
      <>
        <Tbody>
          <Tr key={documentDataExtractor.name}>
            <Td w={32}><Code>{documentDataExtractor.name}</Code></Td>
            <Td w={32}>{documentDataExtractor.prompt}</Td>
            <Td w={32}>{documentDataExtractor.timestamp}</Td>
          </Tr>
        </Tbody>
      </>
    )
  )
}

function DataExtractors() {
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
  // const secBgColor = useColorModeValue('ui.secondary', 'ui.darkSlate')
  
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
                </Tr>
              </Thead>
              {documentDataExtractors.data.map((documentDataExtractor) => (
                <ExtractorExamples documentDataExtractor={documentDataExtractor} is_selected={true}/>
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

  // Get document content extract
  const {
    data: contents,
  } = useQueries({
    queries: (documents?.data || []).map(document => ({
      queryKey: ['document', document.name],
      queryFn: async (): Promise<[Document, string]> => [document, await DocumentsService.readFileAsText({ name: document.name, startPage: 0, endPage: 1 })],
    })),
    combine: (results) => {
      return {
        data: results.reduce((map, result) => {
          if (result.data) {
            const [doc, content] = result.data;
            map.set(doc.name, content);
          }
          return map;
        }, new Map<string, string>()),
        pending: results.some((result) => result.isPending),
      }
    },
  });
  // const secBgColor = useColorModeValue('ui.secondary', 'ui.darkSlate')
  
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
