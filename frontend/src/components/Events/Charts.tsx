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
import StackChart from '@app/components/Common/StackChart'

function hour(timestamp: string): string {
    const date = new Date(timestamp)
    // Extract year, month, day, hour
    const year = date.getUTCFullYear()
    const month = ('0' + (date.getUTCMonth() + 1)).slice(-2) // Months are zero-indexed
    const day = ('0' + date.getUTCDate()).slice(-2)
    const hour = ('0' + date.getUTCHours()).slice(-2)
    // Create a unique key for each hour
    const hourKey = `${year}-${month}-${day} ${hour}:00`
    return hourKey
}

// Compute the volume for each hour-model pair
function volumes(data: EventOut[]): {model: string; hour: string; value: number }[] {
    const result = data.reduce<{model: string; hour: string; value: number }[]>((result, event) => {
        if (event.name === "request") {
            const hourKey = hour(event.timestamp)
            const content = JSON.parse(event.content)
            const modelKey = content.content ? (content.content.model ? content.content.model : "model") : "other"
            result.push({model: modelKey, hour: hourKey, value: 1})
        }
        return result
    }, [])
    return result
}

// function

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
                        <Card mt={4}>
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
                        <Card mt={4}>
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
                                        {
                                            events ? <StackChart data={volumes(events.data)}/> : <Spinner/>
                                        }
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
