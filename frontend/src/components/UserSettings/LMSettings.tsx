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
  Select,
  Checkbox,
} from '@chakra-ui/react'
import { SubmitHandler, useForm } from 'react-hook-form'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'

import { ApiError, SettingCreate, SettingOut, SettingsService } from '@app/client'
import useCustomToast from '@app/hooks/useCustomToast'

const LMTextSetting: React.FC<{title: string; setting: SettingCreate['name']}> = ({title: title, setting: key}) => {
  const queryClient = useQueryClient()
  const color = useColorModeValue('inherit', 'ui.white')
  const showToast = useCustomToast()
  const [editMode, setEditMode] = useState(false)
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
      name: key,
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
      queryClient.invalidateQueries({queryKey: [key]})
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
    <Box py={4} maxW={{ sm: 'full', md: '50%' }} as="form" onSubmit={handleSubmit(onSubmit)}>
      <FormControl>
        <FormLabel color={color} htmlFor="name">
          {title}
        </FormLabel>
        <input type="hidden" value={key} {...register('name')}/>
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
            color={!currentSetting?.content ? 'gray.400' : 'inherit'}
          >
            {currentSetting?.content ? currentSetting?.content.substring(0, 32)+"..." : 'Unset'}
          </Text>
        )}
      </FormControl>
      <Flex mt={4} gap={3}>
        <Button
          size="sm"
          variant="primary"
          onClick={toggleEditMode}
          type={editMode ? 'button' : 'submit'}
          isLoading={editMode ? isSubmitting : false}
          isDisabled={editMode ? !isDirty || !getValues('content') : false}
        >
          {editMode ? 'Save' : 'Edit'}
        </Button>
        {editMode && (
          <Button size="sm" onClick={onCancel} isDisabled={isSubmitting}>
            Cancel
          </Button>
        )}
      </Flex>
    </Box>
  )
}

interface LMConfig {
  pii_removal: "masking" | "replace" | "undefined" | undefined;
  judge_evaluation: boolean;
}

const LMConfigSetting: React.FC = () => {
  const key = 'LM_CONFIG'
  const queryClient = useQueryClient()
  const color = useColorModeValue('inherit', 'ui.white')
  const showToast = useCustomToast()
  const { data: currentSetting } = useQuery<SettingOut>({
    queryKey: [key],
    queryFn: () => SettingsService.readSetting({ name: key })
  })
  const currentConfig: LMConfig = currentSetting ? JSON.parse(currentSetting.content) : {pii_removal: undefined, judge_evaluation: false}
  const {
    register,
    handleSubmit,
    formState: { isSubmitting, isDirty },
  } = useForm<LMConfig>({
    mode: 'onBlur',
    criteriaMode: 'all',
    defaultValues: currentConfig,
  })

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
      queryClient.invalidateQueries({queryKey: [key]})
    },
  })

  const onSubmit: SubmitHandler<LMConfig> = async (data) => {
    if (data.pii_removal == "undefined") {
      data.pii_removal = undefined
    }
    mutation.mutate({name: key, content: JSON.stringify(data)})
  }
  console.log("Bazinga")
  console.log(currentConfig)
  console.log(currentConfig?.pii_removal ? currentConfig?.pii_removal : "masking")
  
  return (currentSetting ? 
    <Box py={4} maxW={{ sm: 'full', md: '50%' }} as="form" onSubmit={handleSubmit(onSubmit)}>
      <FormControl>
        <Box>
          <FormLabel color={color} htmlFor="name">
            PII removal
          </FormLabel>
          <Select
            id="pii_removal"
            {...register('pii_removal')}
            size="md"
            defaultValue={currentConfig.pii_removal ? currentConfig.pii_removal : "masking"}
          >
            <option value="undefined">No</option>
            <option value="masking">PII removal by masking</option>
            <option value="replace">PII removal with replacement</option>
          </Select>
        </Box>
        <Box my={4}>
          <FormLabel color={color} htmlFor="name">
            LLM as a judge
          </FormLabel>
          <Checkbox
            id="judge_evaluation"
            {...register('judge_evaluation')}
            size="md"
            defaultChecked={currentConfig.judge_evaluation}
          >Enable LLM-as-a-Judge evaluation</Checkbox>
        </Box>
      </FormControl>
      <Flex mt={4} gap={3}>
        <Button
          size="sm"
          variant="primary"
          type='submit'
          isLoading={isSubmitting}
          isDisabled={!isDirty}
        >
          Submit
        </Button>
      </Flex>
    </Box> : <Box py={4} maxW={{ sm: 'full', md: '50%' }} as="form" onSubmit={handleSubmit(onSubmit)}>
      <FormControl>
        <Box>
          <FormLabel color={color} htmlFor="name">
            PII removal
          </FormLabel>
          <Select
            id="pii_removal"
            {...register('pii_removal')}
            size="md"
          >
            <option value="undefined">No</option>
            <option value="masking">PII removal by masking</option>
            <option value="replace">PII removal with replacement</option>
          </Select>
        </Box>
        <Box my={4}>
          <FormLabel color={color} htmlFor="name">
            LLM as a judge
          </FormLabel>
          <Checkbox
            id="judge_evaluation"
            {...register('judge_evaluation')}
            size="md"
          >Enable LLM-as-a-Judge evaluation</Checkbox>
        </Box>
      </FormControl>
      <Flex mt={4} gap={3}>
        <Button
          size="sm"
          variant="primary"
          type='submit'
          isLoading={isSubmitting}
          isDisabled={!isDirty}
        >
          Submit
        </Button>
      </Flex>
    </Box>
  )
}

const LMSettings: React.FC = () => {
  return (
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Language Models API Keys and settings
        </Heading>
        <LMTextSetting title="OpenAI API key" setting="OPENAI_API_KEY"></LMTextSetting>
        <LMTextSetting title="Mistral API key" setting="MISTRAL_API_KEY"></LMTextSetting>
        <LMTextSetting title="Anthropic API key" setting="ANTHROPIC_API_KEY"></LMTextSetting>
        <LMConfigSetting/>
      </Container>
  )
}

export default LMSettings

