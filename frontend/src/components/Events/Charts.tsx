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

// Increment a counter for each hour-model pair
function hourModelIncr(counts: { [model: string]: { [hour: string]: number } }, modelKey: string, hourKey: string, value: number): { [model: string]: { [hour: string]: number } } {
    if (!counts[""]) {
        counts[""] = {}
    }
    if (!counts[modelKey]) {
        counts[modelKey] = {}
    }
    if (!counts[""][""]) {
        counts[""][""] = 0
    }
    if (!counts[""][hourKey]) {
        counts[""][hourKey] = 0
    }
    if (!counts[modelKey][""]) {
        counts[modelKey][""] = 0
    }
    if (!counts[modelKey][hourKey]) {
        counts[modelKey][hourKey] = 0
    }
    counts[""][""]+=value
    counts[""][hourKey]+=value
    counts[modelKey][""]+=value
    counts[modelKey][hourKey]+=value
    return counts
}

// Compute the volume for each hour-model pair
function volume(data: EventOut[]): { [model: string]: { [hour: string]: number } } {
    const counts = data.reduce<{ [hour: string]: { [model: string]: number } }>((counts, event) => {
        if (event.name === "request") {
            const hourKey = hour(event.timestamp)
            const content = JSON.parse(event.content)
            const modelKey = content.content ? (content.content.model ? content.content.model : "model") : "other"
            hourModelIncr(counts, modelKey, hourKey, 1)
        }
        return counts
    }, {})
    return counts
}

// Format the data for the graph
function hourModelVolumes(data: EventOut[]): {model: string; hour: string; value: number}[][] {
    const dataVolume = volume(data)
    const models = Object.keys(dataVolume).filter(k => k !== '').sort()
    const hours = Object.keys(dataVolume['']).filter(k => k !== '').sort()
    const result = models.map(model => hours.map(hour => {
        return {model: model, hour: hour, value: (hour in dataVolume[model]) ? dataVolume[model][hour] : 0}
    }))
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

    if (events) {
        console.log(hourModelVolumes(events.data))
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
                                        {
                                            events ? <StackChart data={hourModelVolumes(events.data)}/> : <Spinner/>
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
