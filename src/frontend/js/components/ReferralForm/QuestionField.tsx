import { useMachine } from '@xstate/react';
import React, { useEffect } from 'react';
import { defineMessages, FormattedMessage } from 'react-intl';
import { useUIDSeed } from 'react-uid';
import { assign, Sender } from 'xstate';

import { RichTextFieldMachine, UpdateEvent } from './machines';
import { RichTextField } from 'components/RichText/field';

const messages = defineMessages({
  description: {
    defaultMessage: 'Question for which you are requesting the referral',
    description: 'Description for the question field in the referral form',
    id: 'components.ReferralForm.QuestionField.description',
  },
  label: {
    defaultMessage: 'Referral question',
    description: 'Label for the question field in the referral form',
    id: 'components.ReferralForm.QuestionField.label',
  },
});

interface QuestionFieldProps {
  sendToParent: Sender<UpdateEvent>;
}

export const QuestionField: React.FC<QuestionFieldProps> = ({
  sendToParent,
}) => {
  const seed = useUIDSeed();

  const [state, send] = useMachine(RichTextFieldMachine, {
    actions: {
      setValue: assign({
        value: (_, event) => event.data,
      }),
    },
    guards: {
      isValid: (context) =>
        !!context.value && context.value.textContent.length > 0,
    },
  });

  // Send an update to the parent whenever the state or context changes
  useEffect(() => {
    sendToParent({
      payload: {
        clean: state.matches('cleaned.true'),
        data: JSON.stringify(state.context.value.serializableState),
        valid: state.matches('validation.valid'),
      },
      fieldName: 'question',
      type: 'UPDATE',
    });
  }, [state.value, state.context]);

  return (
    <div className="mb-8">
      <label
        htmlFor={seed('referral-question-label')}
        className="mb-1 font-semibold"
      >
        <FormattedMessage {...messages.label} />
      </label>
      <p
        id={seed('referral-question-description')}
        className="text-gray-600 mt-0 mb-1"
      >
        <FormattedMessage {...messages.description} />
      </p>

      <RichTextField onChange={(e) => send({ type: 'CHANGE', data: e.data })} />
    </div>
  );
};
