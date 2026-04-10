import { z } from 'zod';

import { passwordSchema } from '../../schemas/password.schema';
import { Z } from '../../zod-class';

export class PublicSignupRequestDto extends Z.class({
	email: z.string().trim().email().max(254),
	firstName: z.string().trim().min(1).max(32),
	lastName: z.string().trim().min(1).max(32),
	password: passwordSchema,
	turnstileToken: z.string().trim().optional(),
}) {}
