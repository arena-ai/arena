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
  ButtonGroup,
  Spacer,
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useMemo } from 'react'
import { useQuery, useQueries } from '@tanstack/react-query'

import { ApiError, EventOut, EventsService, UserOut, UsersService } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'
import DownloadButton from '@app/components/Events/DownloadButton'

export const Route = createFileRoute('/_layout/events')({
  component: Events,
})

function format_event(e: EventOut) {
  try {
    if (e.name === "request" || e.name === "modified_request") {
      return format_chat_request(JSON.parse(e.content));
    } else if (e.name === "response" || e.name === "modified_response") {
      return format_chat_response(JSON.parse(e.content));
    } else if (e.name === "user_evaluation" || e.name === "lm_judge_evaluation") {
      return format_evaluation(JSON.parse(e.content));
    } else {
      return format_json(e.content || 'N/A');
    }
  } catch (error) {
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

function format_chat_response(content: { content: { choices: Array<{ message: { role: string; content: string } }> } }) {
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
    <Code>{content}</Code>
  </Box>
}

function Events() {
  const showToast = useCustomToast()
  // Pull events
  const {
    data: events,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['events'],
    queryFn: () => EventsService.readEvents({ limit: 10000 }),
  })
  
  const secBgColor = useColorModeValue('ui.secondary', 'ui.darkSlate')

  // Collect owner ids
  const ownerIds = useMemo(() => {
    const ownerIds = events ? events!.data.map(event => event.owner_id) : [];
    return [...new Set(ownerIds)];
  }, [events]);
  
  // Get owners names
  const {
    data: owners,
  } = useQueries({
    queries: ownerIds.map(ownerId => ({
      queryKey: ['user', ownerId],
      queryFn: async (): Promise<[number, UserOut | undefined]> => [ownerId, await UsersService.readUserById({ userId: ownerId })],
    })),
    combine: (results) => {
      return {
        data: results.reduce((map, result) => {
          if (result.data) {
            const [id, user] = result.data;
            map.set(id, user ? (user.full_name || user.email) : "Unknown");
          }
          return map;
        }, new Map<number, string>()),
        pending: results.some((result) => result.isPending),
      }
    },
  });

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
            <Flex py={8} gap={4} minWidth='max-content' alignItems='center'>
              <Box py='2'>
                <Heading size='sm'>Events</Heading>
              </Box>
              <Spacer />
              <ButtonGroup gap='2'>
              <DownloadButton format='parquet' />
              <DownloadButton format='csv' />
              </ButtonGroup>
            </Flex>
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
                      <Td w={32}>{owners.get(event.owner_id) || "Unknown"}</Td>
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
