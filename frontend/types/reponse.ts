export interface BaseApiReponse<T> {
	success: boolean;
	code: string;
	statusCode: string;
	message: string;
	data: T;
}
