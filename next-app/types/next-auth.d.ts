import NextAuth from "next-auth";
declare module "next-auth" {
	/**
	 * Returned by `useSession`, `getSession` and received as a prop on the `SessionProvider` React Context
	 */
	interface Session {
		/** JWT Access Token to Backend API. */
		backendAccessToken?: string;
	}
}

declare module "next-auth/jwt" {
	/** Returned by the `jwt` callback and `getToken`, when using JWT sessions */
	interface JWT {
		/** Backend Access Token */
		backend_access_token?: string;
	}
}
