export enum UserType {
	SELLER = "SELLER",
	BUYER = "BUYER",
	FARMER = "FARMER",
	SERVICE_PROVIDER = "SERVICE_PROVIDER",
}

export const allowedUserTypes: UserType[] = Object.values(UserType);

export type UserSchema = {
	name: string;
	email: string;
	password: string;
	userType: UserType;
	updatedAt: Date;
	createdAt: Date;
};

export function isValidUserType(value: unknown): value is UserType {
	return (
		typeof value === "string" && allowedUserTypes.includes(value as UserType)
	);
}
