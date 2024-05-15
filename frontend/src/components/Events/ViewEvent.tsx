import React from 'react'
import {
  Button,
  // FormControl,
  // FormErrorMessage,
  // FormLabel,
  // Input,
  Modal,
  // ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
} from '@chakra-ui/react'
import { SubmitHandler, useForm } from 'react-hook-form'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ApiError, EventOut, EventUpdate, EventsService } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'

interface EditEventProps {
  event: EventOut
  isOpen: boolean
  onClose: () => void
}

const EditEvent: React.FC<EditEventProps> = ({ event: event, isOpen, onClose }) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    // register,
    handleSubmit,
    reset,
    formState: { isSubmitting,
      // errors,
      isDirty },
  } = useForm<EventsService>({
    mode: 'onBlur',
    criteriaMode: 'all',
    defaultValues: event,
  })

  const updateEvent = async (data: EventsService) => {
    await EventsService.updateEvent({ id: event.id, requestBody: data })
  }

  const mutation = useMutation({
    mutationFn: updateEvent,
    onSuccess: () => {
      showToast('Success!', 'Item updated successfully.', 'success')
      onClose()
    },
    onError: (err: ApiError) => {
      const errDetail = err.body.detail
      showToast('Something went wrong.', `${errDetail}`, 'error')
    },
    onSettled: () => {
      queryClient.invalidateQueries({queryKey: ['items']})
    },
  })

  const onSubmit: SubmitHandler<EventUpdate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: 'sm', md: 'md' }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Events</ModalHeader>
          <ModalCloseButton />
          {/* <ModalBody pb={6}>
            <FormControl isInvalid={!!errors.id}>
              <FormLabel htmlFor="title">Title</FormLabel>
              <Input
                id="title"
                {...register('title', {
                  required: 'Title is required',
                })}
                type="text"
              />
              {errors.id && (
                <FormErrorMessage>{errors.id.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="description">Description</FormLabel>
              <Input
                id="description"
                {...register('description')}
                placeholder="Description"
                type="text"
              />
            </FormControl>
          </ModalBody> */}
          <ModalFooter gap={3}>
            <Button
              variant="primary"
              type="submit"
              isLoading={isSubmitting}
              isDisabled={!isDirty}
            >
              Save
            </Button>
            <Button onClick={onCancel}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default EditEvent
