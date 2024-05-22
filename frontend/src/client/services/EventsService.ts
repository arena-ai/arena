/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__models__Message } from '../models/app__models__Message';
import type { EventAttribute } from '../models/EventAttribute';
import type { EventAttributeCreate } from '../models/EventAttributeCreate';
import type { EventCreate } from '../models/EventCreate';
import type { EventIdentifier } from '../models/EventIdentifier';
import type { EventOut } from '../models/EventOut';
import type { EventsOut } from '../models/EventsOut';
import type { EventUpdate } from '../models/EventUpdate';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class EventsService {

    /**
     * Read Events
     * Retrieve Events.
     * @returns EventsOut Successful Response
     * @throws ApiError
     */
    public static readEvents({
        skip,
        limit = 100,
    }: {
        skip?: number,
        limit?: number,
    }): CancelablePromise<EventsOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/events/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Event
     * Create new event.
     * @returns EventOut Successful Response
     * @throws ApiError
     */
    public static createEvent({
        requestBody,
    }: {
        requestBody: EventCreate,
    }): CancelablePromise<EventOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/events/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read Event
     * Get event by ID.
     * @returns EventOut Successful Response
     * @throws ApiError
     */
    public static readEvent({
        id,
    }: {
        id: number,
    }): CancelablePromise<EventOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/events/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Event
     * Update an event.
     * @returns EventOut Successful Response
     * @throws ApiError
     */
    public static updateEvent({
        id,
        requestBody,
    }: {
        id: number,
        requestBody: EventUpdate,
    }): CancelablePromise<EventOut> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/events/{id}',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Event
     * Delete an event.
     * @returns app__models__Message Successful Response
     * @throws ApiError
     */
    public static deleteEvent({
        id,
    }: {
        id: number,
    }): CancelablePromise<app__models__Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/events/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read Event By Identifier
     * Get event by identifier.
     * @returns EventOut Successful Response
     * @throws ApiError
     */
    public static readEventByIdentifier({
        identifier,
    }: {
        identifier: string,
    }): CancelablePromise<EventOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/events/identifier/{identifier}',
            path: {
                'identifier': identifier,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Event Identifier
     * Delete an event identifier.
     * @returns app__models__Message Successful Response
     * @throws ApiError
     */
    public static deleteEventIdentifier({
        identifier,
    }: {
        identifier: string,
    }): CancelablePromise<app__models__Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/events/identifier/{identifier}',
            path: {
                'identifier': identifier,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Event Identifier Get
     * Create new event identifier.
     * @returns EventIdentifier Successful Response
     * @throws ApiError
     */
    public static createEventIdentifierGet({
        id,
        identifier,
    }: {
        id: number,
        identifier: string,
    }): CancelablePromise<EventIdentifier> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/events/{id}/identifier/{identifier}',
            path: {
                'id': id,
                'identifier': identifier,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Event Identifier
     * Create new event identifier.
     * @returns EventIdentifier Successful Response
     * @throws ApiError
     */
    public static createEventIdentifier({
        requestBody,
    }: {
        requestBody: EventIdentifier,
    }): CancelablePromise<EventIdentifier> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/events/identifier',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Event Attribute Get
     * Create new event attribute.
     * @returns EventAttribute Successful Response
     * @throws ApiError
     */
    public static eventAttribute({
        id,
        name,
    }: {
        id: number,
        name: string,
    }): CancelablePromise<EventAttribute> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/events/{id}/attribute/{name}',
            path: {
                'id': id,
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Event Attribute
     * Delete an event attribute.
     * @returns app__models__Message Successful Response
     * @throws ApiError
     */
    public static deleteEventAttribute({
        id,
        name,
    }: {
        id: number,
        name: string,
    }): CancelablePromise<app__models__Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/events/{id}/attribute/{name}',
            path: {
                'id': id,
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Event Attribute Get With Value
     * Create new event attribute.
     * @returns EventAttribute Successful Response
     * @throws ApiError
     */
    public static eventAttributeValue({
        id,
        name,
        value,
    }: {
        id: number,
        name: string,
        value: string,
    }): CancelablePromise<EventAttribute> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/events/{id}/attribute/{name}/{value}',
            path: {
                'id': id,
                'name': name,
                'value': value,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Event Attribute
     * Create new event attribute.
     * @returns EventAttribute Successful Response
     * @throws ApiError
     */
    public static createEventAttribute({
        requestBody,
    }: {
        requestBody: EventAttributeCreate,
    }): CancelablePromise<EventAttribute> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/events/attribute',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Download Events
     * Retrieve Events.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static downloadEvents({
        format,
        skip,
        limit = 1000000,
    }: {
        format: 'parquet' | 'csv',
        skip?: number,
        limit?: number,
    }): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/events/download/{format}',
            path: {
                'format': format,
            },
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
