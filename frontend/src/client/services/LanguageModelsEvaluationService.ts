/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Evaluation } from '../models/Evaluation';
import type { Event } from '../models/Event';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class LanguageModelsEvaluationService {

    /**
     * Evaluation
     * @returns Event Successful Response
     * @throws ApiError
     */
    public static evaluation({
        requestBody,
    }: {
        requestBody: Evaluation,
    }): CancelablePromise<Event> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/lm/evaluation',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Evaluation Get
     * @returns Event Successful Response
     * @throws ApiError
     */
    public static evaluationGet({
        identifier,
        score,
    }: {
        identifier: string,
        score: number,
    }): CancelablePromise<Event> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/lm/evaluation/{identifier}/{score}',
            path: {
                'identifier': identifier,
                'score': score,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
