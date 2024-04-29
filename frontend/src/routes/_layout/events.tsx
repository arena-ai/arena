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
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from 'react-query'

import { ApiError, EventsService } from '../../client'
import EventsSummary from '../../components/Common/EventsSummary'
import useCustomToast from '../../hooks/useCustomToast'

export const Route = createFileRoute('/_layout/events')({
  component: Events,
})

function Events() {
  const showToast = useCustomToast()
  const {
    data: events,
    isLoading,
    isError,
    error,
  } = useQuery('events', () => EventsService.readEvents({}))

  if (isError) {
    const errDetail = (error as ApiError).body?.detail
    showToast('Something went wrong.', `${errDetail}`, 'error')
  }

  return (
    <>
      {isLoading ? (
        // TODO: Add skeleton
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        events && (
          <Container maxW="full">
            <Heading
              size="lg"
              textAlign={{ base: 'center', md: 'left' }}
              pt={12}
            >
              Events
            </Heading>
            <EventsSummary/>
            <TableContainer>
              <Table size={{ base: 'sm', md: 'md' }}>
                <Thead>
                  <Tr>
                    <Th>Id</Th>
                    <Th>Name</Th>
                    <Th>Timestamp</Th>
                    <Th>Content</Th>
                    <Th>Parent id</Th>
                    <Th>Owner</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {events.data.map((event) => (
                    <Tr key={event.id}>
                      <Td>{event.id}</Td>
                      <Td>{event.name}</Td>
                      <Td>{event.timestamp}</Td>
                      <Td color={!event.content ? 'gray.400' : 'inherit'}>
                        {JSON.parse(event.content) || 'N/A'}
                      </Td>
                      <Td>{event.parent_id}</Td>
                      <Td>{event.owner_id}</Td>
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

export default Events
