import { createAuth } from "better-auth";

export const auth = createAuth({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:8000",
  plugins: [],
});

export const signIn = async (email: string, password: string) => {
  return auth.signIn.create({
    body: {
      email,
      password,
    },
  });
};

export const signUp = async (name: string, email: string, password: string) => {
  return auth.signUp.create({
    body: {
      name,
      email,
      password,
    },
  });
};

export const signOut = async () => {
  return auth.signOut();
};

export const getSession = async () => {
  return auth.getSession();
};

