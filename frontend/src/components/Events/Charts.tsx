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
import { useRef, useEffect } from 'react'

import { ApiError, EventOut, EventsService } from '@app/client'

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
function hourModelIncr(counts: { [hour: string]: { [model: string]: number } }, hourKey: string, modelKey: string, value: number): { [hour: string]: { [model: string]: number } } {
    if (!counts[""]) {
        counts[""] = {}
    }
    if (!counts[hourKey]) {
        counts[hourKey] = {}
    }
    if (!counts[""][""]) {
        counts[""][""] = 0
    }
    if (!counts[""][modelKey]) {
        counts[""][modelKey] = 0
    }
    if (!counts[hourKey][""]) {
        counts[hourKey][""] = 0
    }
    if (!counts[hourKey][modelKey]) {
        counts[hourKey][modelKey] = 0
    }
    counts[""][""]+=value
    counts[""][modelKey]+=value
    counts[hourKey][""]+=value
    counts[hourKey][modelKey]+=value
    return counts
}

// Compute the volume for each hour-model pair
function volume(data: EventOut[]): { [hour: string]: { [model: string]: number } } {
    const counts = data.reduce<{ [hour: string]: { [model: string]: number } }>((counts, event) => {
        if (event.name === "request") {
            const hourKey = hour(event.timestamp)
            const content = JSON.parse(event.content)
            const modelKey = content.content ? (content.content.model ? content.content.model : "model") : "other"
            hourModelIncr(counts, hourKey, modelKey, 1)
        }
        return counts
    }, {})
    return counts
}

function hourModelVolumes(data: EventOut[]): {hour: string; model: string; value: number}[][] {
    const dataVolume = volume(data)
    const hours = Object.keys(dataVolume).filter(k => k !== '').sort()
    const models = Object.keys(dataVolume['']).filter(k => k !== '').sort()
    const result = models.map(model => hours.map(hour => {
        return {hour: hour, model: model, value: (model in dataVolume[hour]) ? dataVolume[hour][model] : 0}
    }))
    return result
}

function Charts() {
    //refs
    const volumeSvg = useRef();
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
                                        <svg ref={volumeSvg}/>
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
