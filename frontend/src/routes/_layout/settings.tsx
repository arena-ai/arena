import {
  Container,
  Heading,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
} from '@chakra-ui/react'
import { createFileRoute } from '@tanstack/react-router'
import { useQueryClient } from '@tanstack/react-query'

import { UserOut } from '@app/client'
import Appearance from '@app/components/UserSettings/Appearance'
import ChangePassword from '@app/components/UserSettings/ChangePassword'
import DeleteAccount from '@app/components/UserSettings/DeleteAccount'
import UserInformation from '@app/components/UserSettings/UserInformation'
import LMSettings from '@app/components/UserSettings/LMSettings'

const tabsConfig = [
  { title: 'My profile', component: UserInformation },
  { title: 'Language Models', component: LMSettings },
  { title: 'Password', component: ChangePassword },
  { title: 'Appearance', component: Appearance },
  { title: 'Danger zone', component: DeleteAccount },
]

export const Route = createFileRoute('/_layout/settings')({
  component: UserSettings,
})

function UserSettings() {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserOut>(['currentUser'])
  const finalTabs = currentUser?.is_superuser
    ? tabsConfig.slice(0, 4)
    : tabsConfig

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: 'center', md: 'left' }} py={12}>
        User Settings
      </Heading>
      <Tabs variant="enclosed">
        <TabList>
          {finalTabs.map((tab, index) => (
            <Tab key={index}>{tab.title}</Tab>
          ))}
        </TabList>
        <TabPanels>
          {finalTabs.map((tab, index) => (
            <TabPanel key={index}>
              <tab.component />
            </TabPanel>
          ))}
        </TabPanels>
      </Tabs>
    </Container>
  )
}

export default UserSettings
