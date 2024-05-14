import React from 'react'
import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Button,
} from '@chakra-ui/react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from 'react-query'

import { UsersService } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'

interface DeleteProps {
  type: string
  id: number
  isOpen: boolean
  onClose: () => void
}

const Delete: React.FC<DeleteProps> = ({ type, id, isOpen, onClose }) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const cancelRef = React.useRef<HTMLButtonElement | null>(null)
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteEntity = async (id: number) => {
    if (type === 'User') {
      await UsersService.deleteUser({ userId: id })
    } else {
      throw new Error(`Unexpected type: ${type}`)
    }
  }

  const mutation = useMutation(deleteEntity, {
    onSuccess: () => {
      showToast(
        'Success',
        `The ${type.toLowerCase()} was deleted successfully.`,
        'success',
      )
      onClose()
    },
    onError: () => {
      showToast(
        'An error occurred.',
        `An error occurred while deleting the ${type.toLowerCase()}.`,
        'error',
      )
    },
    onSettled: () => {
      queryClient.invalidateQueries(type === 'Item' ? 'items' : 'users')
    },
  })

  const onSubmit = async () => {
    mutation.mutate(id)
  }

  return (
    <>
      <AlertDialog
        isOpen={isOpen}
        onClose={onClose}
        leastDestructiveRef={cancelRef}
        size={{ base: 'sm', md: 'md' }}
        isCentered
      >
        <AlertDialogOverlay>
          <AlertDialogContent as="form" onSubmit={handleSubmit(onSubmit)}>
            <AlertDialogHeader>Delete {type}</AlertDialogHeader>

            <AlertDialogBody>
              {type === 'User' && (
                <span>
                  All items associated with this user will also be{' '}
                  <strong>permantly deleted. </strong>
                </span>
              )}
              Are you sure? You will not be able to undo this action.
            </AlertDialogBody>

            <AlertDialogFooter gap={3}>
              <Button variant="danger" type="submit" isLoading={isSubmitting}>
                Delete
              </Button>
              <Button
                ref={cancelRef}
                onClick={onClose}
                isDisabled={isSubmitting}
              >
                Cancel
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  )
}

export default Delete
