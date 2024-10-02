import {
  Container,
  Flex,
  Heading,
  Spinner,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  // useColorModeValue,
  Box,
  Spacer,
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'

import { ApiError, DocumentsService } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'
// import UploadForm from '@app/components/Documents/UploadForm'

export const Route = createFileRoute('/_layout/documents')({
  component: Documents,
})

function Documents() {
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
              Documents
            </Heading>
            <Flex py={8} gap={4} minWidth='max-content' alignItems='center'>
              <Box p='2'>
                <Heading size='sm'>Documents</Heading>
              </Box>
              <Spacer />
              {/* Add an umpload zone here */}
            </Flex>
            <TableContainer>
              <Table size={{ base: 'sm', md: 'md' }} whiteSpace="normal">
                <Thead>
                  <Tr>
                    <Th>Filename</Th>
                    <Th>Content Type</Th>
                    <Th>Timestamp</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {documents.data.map((document) => (
                    <Tr key={document.name}>
                      <Td w={32}>{document.filename}</Td>
                      <Td w={32}>{document.content_type}</Td>
                      <Td w={32}>{document.name}</Td>
                      {/* <Td w={32}>{event.name}</Td>
                      <Td w={64}>{event.timestamp.slice(0, 19)}</Td>
                      <Td color={!event.content ? 'gray.400' : 'inherit'}>
                        {format_event(event)}
                      </Td>
                      <Td w={32}>{event.parent_id}</Td>
                      <Td w={32}>{owners.get(event.owner_id) || "Unknown"}</Td> */}
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          </Container>
        )
      )}
    </>
  )
}

export default Documents
