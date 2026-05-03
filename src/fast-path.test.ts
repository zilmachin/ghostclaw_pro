import { describe, it, expect } from 'vitest';

import { shouldBypassFastPath } from './fast-path.js';

describe('shouldBypassFastPath — true when message starts with a memory-write verb', () => {
  it('matches imperative forms at the start', () => {
    expect(shouldBypassFastPath('remember that I like coffee')).toBe(true);
    expect(shouldBypassFastPath('Log this: the build is green')).toBe(true);
    expect(shouldBypassFastPath('save this for later')).toBe(true);
    expect(shouldBypassFastPath("don't forget the meeting")).toBe(true);
    expect(shouldBypassFastPath('dont forget the meeting')).toBe(true);
    expect(shouldBypassFastPath('note that prod is down')).toBe(true);
    expect(shouldBypassFastPath('file this under research')).toBe(true);
    expect(shouldBypassFastPath('write this down')).toBe(true);
    expect(shouldBypassFastPath('write down the error code')).toBe(true);
    expect(shouldBypassFastPath('store this for the record')).toBe(true);
    expect(shouldBypassFastPath('keep in mind the timezone')).toBe(true);
    expect(shouldBypassFastPath('for future reference, API is down')).toBe(
      true,
    );
    expect(shouldBypassFastPath('make a note of this')).toBe(true);
    expect(shouldBypassFastPath('take a note on the design')).toBe(true);
    expect(shouldBypassFastPath('bank this fact')).toBe(true);
  });

  it('is case insensitive', () => {
    expect(shouldBypassFastPath('REMEMBER this')).toBe(true);
    expect(shouldBypassFastPath('Note That the build passed')).toBe(true);
  });

  it('tolerates leading punctuation/whitespace', () => {
    expect(shouldBypassFastPath('  remember to ping Alice')).toBe(true);
    expect(shouldBypassFastPath('"remember the milk"')).toBe(true);
  });
});

describe('shouldBypassFastPath — false for conversational uses', () => {
  it('does not match normal chat', () => {
    expect(shouldBypassFastPath('hey, how are you?')).toBe(false);
    expect(shouldBypassFastPath('what is the weather today')).toBe(false);
    expect(shouldBypassFastPath("what's on my roadmap")).toBe(false);
    expect(shouldBypassFastPath('can you summarise the commits')).toBe(false);
    expect(shouldBypassFastPath('tell me about the new model')).toBe(false);
  });

  it('does not false-positive on the verb appearing mid-sentence', () => {
    // "I don't remember…" is description, not a memory-write request.
    expect(shouldBypassFastPath("I don't remember seeing that")).toBe(false);
    expect(shouldBypassFastPath('Yeah, save that for later maybe')).toBe(false);
    expect(shouldBypassFastPath('did you note the timestamp?')).toBe(false);
    expect(shouldBypassFastPath('he said to keep in mind the deadline')).toBe(
      false,
    );
    expect(shouldBypassFastPath('I want to file this under boring')).toBe(
      false,
    );
  });

  it('does not match different tenses', () => {
    expect(shouldBypassFastPath('duly noted, moving on')).toBe(false);
    expect(shouldBypassFastPath('I remembered the password')).toBe(false);
    expect(shouldBypassFastPath('she logged the bug')).toBe(false);
  });
});
