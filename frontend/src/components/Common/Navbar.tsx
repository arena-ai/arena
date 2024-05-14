import React from 'react'
import { Button, Flex, Icon, useDisclosure } from '@chakra-ui/react'
import { FaPlus } from 'react-icons/fa'

import AddUser from '@app/components/Admin/AddUser'

interface NavbarProps {
  type: string
}

const Navbar: React.FC<NavbarProps> = ({ type }) => {
  const addUserModal = useDisclosure()

  return (
    <>
      <Flex py={8} gap={4}>
        {/* TODO: Complete search functionality */}
        {/* <InputGroup w={{ base: '100%', md: 'auto' }}>
                    <InputLeftElement pointerEvents='none'>
                        <Icon as={FaSearch} color='gray.400' />
                    </InputLeftElement>
                    <Input type='text' placeholder='Search' fontSize={{ base: 'sm', md: 'inherit' }} borderRadius='8px' />
                </InputGroup> */}
        <Button
          variant="primary"
          gap={1}
          fontSize={{ base: 'sm', md: 'inherit' }}
          onClick={type === 'User' ? addUserModal.onOpen : () => null}
        >
          <Icon as={FaPlus} /> Add {type}
        </Button>
        <AddUser isOpen={addUserModal.isOpen} onClose={addUserModal.onClose} />
      </Flex>
    </>
  )
}

export default Navbar
