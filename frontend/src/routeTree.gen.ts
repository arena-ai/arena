/* prettier-ignore-start */

/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file is auto-generated by TanStack Router

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as ResetPasswordImport } from './routes/reset-password'
import { Route as RecoverPasswordImport } from './routes/recover-password'
import { Route as LoginImport } from './routes/login'
import { Route as LayoutImport } from './routes/_layout'
import { Route as LayoutIndexImport } from './routes/_layout/index'
import { Route as LayoutSettingsImport } from './routes/_layout/settings'
import { Route as LayoutEventsImport } from './routes/_layout/events'
import { Route as LayoutDocumentsImport } from './routes/_layout/documents'
import { Route as LayoutDocumentDataExtractorsImport } from './routes/_layout/document-data-extractors'
import { Route as LayoutAdminImport } from './routes/_layout/admin'

// Create/Update Routes

const ResetPasswordRoute = ResetPasswordImport.update({
  path: '/reset-password',
  getParentRoute: () => rootRoute,
} as any)

const RecoverPasswordRoute = RecoverPasswordImport.update({
  path: '/recover-password',
  getParentRoute: () => rootRoute,
} as any)

const LoginRoute = LoginImport.update({
  path: '/login',
  getParentRoute: () => rootRoute,
} as any)

const LayoutRoute = LayoutImport.update({
  id: '/_layout',
  getParentRoute: () => rootRoute,
} as any)

const LayoutIndexRoute = LayoutIndexImport.update({
  path: '/',
  getParentRoute: () => LayoutRoute,
} as any)

const LayoutSettingsRoute = LayoutSettingsImport.update({
  path: '/settings',
  getParentRoute: () => LayoutRoute,
} as any)

const LayoutEventsRoute = LayoutEventsImport.update({
  path: '/events',
  getParentRoute: () => LayoutRoute,
} as any)

const LayoutDocumentsRoute = LayoutDocumentsImport.update({
  path: '/documents',
  getParentRoute: () => LayoutRoute,
} as any)

const LayoutDocumentDataExtractorsRoute =
  LayoutDocumentDataExtractorsImport.update({
    path: '/document-data-extractors',
    getParentRoute: () => LayoutRoute,
  } as any)

const LayoutAdminRoute = LayoutAdminImport.update({
  path: '/admin',
  getParentRoute: () => LayoutRoute,
} as any)

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/_layout': {
      preLoaderRoute: typeof LayoutImport
      parentRoute: typeof rootRoute
    }
    '/login': {
      preLoaderRoute: typeof LoginImport
      parentRoute: typeof rootRoute
    }
    '/recover-password': {
      preLoaderRoute: typeof RecoverPasswordImport
      parentRoute: typeof rootRoute
    }
    '/reset-password': {
      preLoaderRoute: typeof ResetPasswordImport
      parentRoute: typeof rootRoute
    }
    '/_layout/admin': {
      preLoaderRoute: typeof LayoutAdminImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/document-data-extractors': {
      preLoaderRoute: typeof LayoutDocumentDataExtractorsImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/documents': {
      preLoaderRoute: typeof LayoutDocumentsImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/events': {
      preLoaderRoute: typeof LayoutEventsImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/settings': {
      preLoaderRoute: typeof LayoutSettingsImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/': {
      preLoaderRoute: typeof LayoutIndexImport
      parentRoute: typeof LayoutImport
    }
  }
}

// Create and export the route tree

export const routeTree = rootRoute.addChildren([
  LayoutRoute.addChildren([
    LayoutAdminRoute,
    LayoutDocumentDataExtractorsRoute,
    LayoutDocumentsRoute,
    LayoutEventsRoute,
    LayoutSettingsRoute,
    LayoutIndexRoute,
  ]),
  LoginRoute,
  RecoverPasswordRoute,
  ResetPasswordRoute,
])

/* prettier-ignore-end */
