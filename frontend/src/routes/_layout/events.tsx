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
  Text,
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from 'react-query'

import { ApiError, EventOut, EventsService } from '../../client'
import EventsSummary from '../../components/Common/EventsSummary'
import useCustomToast from '../../hooks/useCustomToast'

export const Route = createFileRoute('/_layout/events')({
  component: Events,
})

function format_event(e: EventOut) {
  if (e.name === "LogRequest") {
    return format_chat_request(JSON.parse(e.content));
  } else if (e.name === "LogResponse") {
    return format_chat_response(JSON.parse(e.content));
  } else if (e.name === "UserEvaluation" || e.name === "LMJudgeEvaluation") {
    return format_evaluation(JSON.parse(e.content));
  } else {
    return <div>{e.content || 'N/A'}</div>
  }
}

function format_chat_request(content: { content: { model: string; messages: Array<{ role: string; content: string }> } }) {
  return <div>
    <b>model</b>: {content.content.model}
    {content.content.messages.map((message: { role: string; content: string }, index: number) => <Text key={index}>
    <b>{message.role}</b>: {message.content}
  </Text>)}</div>;
}

function format_chat_response(content: { content: { choices: Array<{ message: { role: string; content: string }}> } }) {
  return <div>{content.content.choices.map((choice, index: number) => <div key={index}>
    <Text><b>{choice.message.role}</b>: {choice.message.content}</Text>
  </div>)}</div>;
}

function format_evaluation(content: { type: string, value: number }) {
  return <div>
    <Text><b>{content.type}</b>: {content.value}</Text>
  </div>;
}

// function format_json(content) {
//   return <div className="w-96 max-h-12 truncate hover:max-h-fit"><pre>{JSON.stringify(content, null, 2)}</pre></div>;
// }

// function format_user_id(id: number) {
//   if (users) {
//       const user = users.find((user) => user?.id===id);
//       return user?.full_name || user?.email || `${id}`;
//   } else {
//       return `${id}`;
//   }
// }

function Events() {
  const showToast = useCustomToast()
  const {
    data: events,
    isLoading,
    isError,
    error,
  } = useQuery('events', () => EventsService.readEvents({limit: 10000}))

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
                      <Td color={!event.content ? 'gray.400' : 'inherit'} maxWidth={512} overflowX="scroll">
                        {format_event(event)}
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
