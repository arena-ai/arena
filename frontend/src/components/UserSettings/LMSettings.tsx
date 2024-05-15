import React, { useState } from 'react'
import {
  Box,
  Button,
  Container,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Text,
  useColorModeValue,
} from '@chakra-ui/react'
import { SubmitHandler, useForm } from 'react-hook-form'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'

import { ApiError, SettingCreate, SettingOut, SettingsService } from '@app/client'
import useAuth from '@app/hooks/useAuth'
import useCustomToast from '@app/hooks/useCustomToast'

const LMTextSetting: React.FC<{setting: SettingCreate['name']}> = ({setting: key}) => {
  const queryClient = useQueryClient()
  const color = useColorModeValue('inherit', 'ui.white')
  const showToast = useCustomToast()
  const [editMode, setEditMode] = useState(false)
  const { user: currentUser } = useAuth()
  const { data: currentSetting } = useQuery<SettingOut>({
    queryKey: [key],
    queryFn: () => SettingsService.readSetting({ name: key })
  })
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { isSubmitting, isDirty },
  } = useForm<SettingCreate>({
    mode: 'onBlur',
    criteriaMode: 'all',
    defaultValues: {
      content: currentSetting ? currentSetting.content : "",
    },
  })

  const toggleEditMode = () => {
    setEditMode(!editMode)
  }

  const updateSetting = async (data: SettingCreate) => {
    await SettingsService.createSetting({ requestBody: data })
  }

  const mutation = useMutation({
    mutationFn: updateSetting,
    onSuccess: () => {
      showToast('Success!', 'User updated successfully.', 'success')
    },
    onError: (err: ApiError) => {
      const errDetail = err.body.detail
      showToast('Something went wrong.', `${errDetail}`, 'error')
    },
    onSettled: () => {
      queryClient.invalidateQueries({queryKey: ['settings']})
    },
  })

  const onSubmit: SubmitHandler<SettingCreate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    toggleEditMode()
  }

  return (
    <>
      <Container maxW="full" as="form" onSubmit={handleSubmit(onSubmit)}>
        <Heading size="sm" py={4}>
          User Information
        </Heading>
        <Box w={{ sm: 'full', md: '50%' }}>
          <FormControl>
            <FormLabel color={color} htmlFor="name">
              {key}
            </FormLabel>
            {editMode ? (
              <Input
                id="name"
                {...register('content', { maxLength: 100 })}
                type="text"
                size="md"
              />
            ) : (
              <Text
                size="md"
                py={2}
                color={!currentUser?.full_name ? 'gray.400' : 'inherit'}
              >
                {currentUser?.full_name || 'N/A'}
              </Text>
            )}
          </FormControl>
          <Flex mt={4} gap={3}>
            <Button
              variant="primary"
              onClick={toggleEditMode}
              type={editMode ? 'button' : 'submit'}
              isLoading={editMode ? isSubmitting : false}
              isDisabled={editMode ? !isDirty || !getValues('content') : false}
            >
              {editMode ? 'Save' : 'Edit'}
            </Button>
            {editMode && (
              <Button onClick={onCancel} isDisabled={isSubmitting}>
                Cancel
              </Button>
            )}
          </Flex>
        </Box>
      </Container>
    </>
  )
}

export const OpenaiApiToken: React.FC = () => <LMTextSetting setting='OPENAI_API_KEY'></LMTextSetting>

