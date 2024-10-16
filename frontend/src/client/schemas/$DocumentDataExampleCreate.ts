/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DocumentDataExampleCreate = {
    properties: {
        document_id: {
            type: 'string',
            isRequired: true,
        },
        data: {
            type: 'dictionary',
            contains: {
                type: 'any-of',
                contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
            },
            isRequired: true,
        },
        document_data_extractor_id: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        start_page: {
            type: 'number',
        },
        end_page: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
