import React from 'react'
import { Menu, MenuButton, MenuList, MenuItem, IconButton, HStack, Text } from '@chakra-ui/react'
import { ChevronDownIcon } from '@chakra-ui/icons'
import { useLanguage, Language } from '../contexts/LanguageContext'

export const LanguageSelector: React.FC = () => {
  const { language, setLanguage } = useLanguage()

  const languages: { code: Language; name: string; flag: string }[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  ]

  const currentLang = languages.find(l => l.code === language) || languages[1]

  return (
    <Menu>
      <MenuButton
        as={IconButton}
        icon={
          <HStack spacing={1}>
            <Text fontSize="lg">{currentLang.flag}</Text>
            <ChevronDownIcon />
          </HStack>
        }
        variant="ghost"
        aria-label="Select language"
        size="sm"
      />
      <MenuList>
        {languages.map(lang => (
          <MenuItem
            key={lang.code}
            onClick={() => setLanguage(lang.code)}
            bg={language === lang.code ? 'rgba(0, 212, 255, 0.1)' : undefined}
            _hover={{ bg: 'rgba(0, 212, 255, 0.2)' }}
          >
            <HStack spacing={2}>
              <Text fontSize="lg">{lang.flag}</Text>
              <Text>{lang.name}</Text>
            </HStack>
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  )
}
