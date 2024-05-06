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
  Code,
  useColorModeValue,
  Box,
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
  try {
    if (e.name === "request" || e.name === "modified_request") {
      return format_chat_request(JSON.parse(e.content));
    } else if (e.name === "response") {
      return format_chat_response(JSON.parse(e.content));
    } else if (e.name === "user_evaluation" || e.name === "lm_judge_evaluation") {
      return format_evaluation(JSON.parse(e.content));
    } else {
      return format_json(e.content || 'N/A');
    }
  } catch(error) {
    return format_json(e.content || 'N/A');
  }
}

function format_chat_request(content: { content: { model: string; messages: Array<{ role: string; content: string }> } }) {
  return <Box>
    <b>model</b>: {content.content.model}
    {content.content.messages.map((message: { role: string; content: string }, index: number) => <Text key={index}>
    <b>{message.role}</b>: {message.content}
  </Text>)}</Box>;
}

function format_chat_response(content: { content: { choices: Array<{ message: { role: string; content: string }}> } }) {
  return <Box>
    {content.content.choices.map((choice, index: number) => <Text key={index}>
    <b>{choice.message.role}</b>: {choice.message.content}
  </Text>)}</Box>;
}

function format_evaluation(content: { type: string, value: number }) {
  return <Box>
    <Text><b>{content.type}</b>: {content.value}</Text>
  </Box>;
}

function format_json(content: string) {
  return <Box>
      <Code w={1024}>{JSON.stringify(content, null, 2)}</Code>;
    </Box>
}

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
  const secBgColor = useColorModeValue('ui.secondary', 'ui.darkSlate')

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
              <Table size={{ base: 'sm', md: 'md' }} whiteSpace="normal">
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
                    <Tr key={event.id} bgColor={event.parent_id ? 'inherit' : secBgColor}>
                      <Td w={32}>{event.id}</Td>
                      <Td w={32}>{event.name}</Td>
                      <Td w={64}>{event.timestamp.slice(0, 19)}</Td>
                      <Td color={!event.content ? 'gray.400' : 'inherit'}>
                        {format_event(event)}
                      </Td>
                      <Td w={32}>{event.parent_id}</Td>
                      <Td w={32}>{event.owner_id}</Td>
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
