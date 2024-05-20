import {
    Flex,
    Heading,
    Spinner,
    Text,
    useColorModeValue,
    Box,
    Card,
    CardHeader,
    CardBody,
    StackDivider,
    Stack,
} from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'

import { ApiError, EventOut, EventsService } from '@app/client'

function volume(data: EventOut[]): Map<string, number> {
    const counts = new Map<string, number>()
    console.log(data)
    return counts
}

function Charts() {
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

    if (isError) {
        const errDetail = (error as ApiError).body?.detail
        console.warn('Something went wrong.', `${errDetail}`, 'error')
    }

    console.log(volume(events!.data.slice(0,2)))
    return (
        <>
            {isLoading ? (
                // TODO: Add skeleton
                <Flex justify="center" align="center" height="100vh" width="full">
                    <Spinner size="xl" color="ui.main" />
                </Flex>
            ) : (
                events && (
                    <>
                        <Heading>Activity</Heading>
                        <Card mt={4} bgColor={secBgColor}>
                            <CardHeader>
                                <Heading size='md'>Volume</Heading>
                            </CardHeader>

                            <CardBody>
                                <Stack divider={<StackDivider />} spacing='4'>
                                    <Box>
                                        <Heading size='xs' textTransform='uppercase'>
                                            Number of events by model
                                        </Heading>
                                        <Text pt='2' fontSize='sm'>
                                            View a summary of all your clients over the last month.
                                        </Text>
                                    </Box>
                                    <Box>
                                    </Box>
                                </Stack>
                            </CardBody>
                        </Card>
                        <Card mt={4} bgColor={secBgColor}>
                            <CardHeader>
                                <Heading size='md'>Score</Heading>
                            </CardHeader>

                            <CardBody>
                                <Stack divider={<StackDivider />} spacing='4'>
                                    <Box>
                                        <Heading size='xs' textTransform='uppercase'>
                                        Summary
                                        </Heading>
                                        <Text pt='2' fontSize='sm'>
                                        View a summary of all your clients over the last month.
                                        </Text>
                                    </Box>
                                    <Box>
                                        
                                    </Box>
                                </Stack>
                            </CardBody>
                        </Card>
                    </>
                )
            )}
        </>
    )
}

export default Charts
