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
  // useColorModeValue,
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useQueries } from '@tanstack/react-query'

import { ApiError, DocumentsService, Document, DocumentDataExtractorsService, DocumentDataExtractorOut, DocumentDataExtractorsOut } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'

export const Route = createFileRoute('/_layout/document-data-extractors')({
  component: DocumentDataExtractors,
})

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
          <Box>
            <Heading size='sm'>Data Extractors</Heading>
            <TableContainer>
              <Table size={{ base: 'sm', md: 'md' }} whiteSpace="normal">
                <Thead>
                  <Tr>
                    <Th>Name</Th>
                    <Th>Prompt</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {documentDataExtractors.data.map((documentDataExtractor) => (
                    <Tr key={documentDataExtractor.name}>
                      <Td w={16}><Code>{documentDataExtractor.name}</Code></Td>
                      <Td w={32}>{documentDataExtractor.prompt}</Td>
                    </Tr>
                  ))}
                </Tbody>
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
